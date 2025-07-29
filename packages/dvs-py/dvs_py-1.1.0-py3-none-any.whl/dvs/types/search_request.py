import collections
import logging
import typing

import openai
import openai_embeddings_model as oai_emb_model
import pydantic

import dvs.utils.is_ as IS
import dvs.utils.to as TO
from dvs.types.encoding_type import EncodingType
from dvs.utils.dummies import dummy_httpx_response

logger = logging.getLogger(__name__)


class SearchRequest(pydantic.BaseModel):
    """
    Represents a single search request for vector similarity search.

    This class encapsulates the parameters needed to perform a vector similarity search
    in the DuckDB VSS API. It allows users to specify the query, the number of results
    to return, whether to include the embedding in the results, and the encoding type of the query.

    Attributes:
        query (Union[Text, List[float]]): The search query, which can be either a text string,
            a pre-computed vector embedding as a list of floats, or a base64 encoded string
            representing a vector. The interpretation of this field depends on the `encoding` attribute.
        top_k (int): The maximum number of results to return. Defaults to 5.
        with_embedding (bool): Whether to include the embedding vector in the search results.
            Defaults to False to reduce response size.
        encoding (Optional[EncodingType]): The encoding type for the query. Can be one of:
            - None (default): Assumes plaintext if query is a string, or a vector if it's a list of floats.
            - EncodingType.PLAINTEXT: Treats the query as plaintext to be converted to a vector.
            - EncodingType.BASE64: Treats the query as a base64 encoded vector.
            - EncodingType.VECTOR: Explicitly specifies that the query is a pre-computed vector.

    Example:
        >>> request = SearchRequest(query="How does AI work?", top_k=10, with_embedding=True)
        >>> print(request)
        SearchRequest(query='How does AI work?', top_k=10, with_embedding=True, encoding=None)

        >>> vector_request = SearchRequest(query=[0.1, 0.2, 0.3], top_k=5, encoding=EncodingType.VECTOR)
        >>> print(vector_request)
        SearchRequest(query=[0.1, 0.2, 0.3], top_k=5, with_embedding=False, encoding=<EncodingType.VECTOR: 'vector'>)

    Note:
        - When `encoding` is None or EncodingType.PLAINTEXT, and `query` is a string, it will be converted
          to a vector embedding using the configured embedding model.
        - When `encoding` is EncodingType.BASE64, the `query` should be a base64 encoded string
          representing a vector, which will be decoded before search.
        - When `encoding` is EncodingType.VECTOR or `query` is a list of floats, it's assumed
          to be a pre-computed embedding vector.
        - The `encoding` field provides flexibility for clients to send queries in different formats,
          allowing for optimization of request size and processing time.
    """  # noqa: E501

    query: typing.Union[typing.Text, typing.List[float]] = pydantic.Field(
        ...,
        description="The search query as text or a pre-computed vector embedding.",
    )
    top_k: int = pydantic.Field(
        default=5,
        description="The maximum number of results to return.",
    )
    with_embedding: bool = pydantic.Field(
        default=False,
        description="Whether to include the embedding in the result.",
    )
    encoding: typing.Optional[EncodingType] = pydantic.Field(
        default=None,
        description="The encoding type for the query.",
    )

    @classmethod
    async def to_vectors(
        cls,
        search_requests: typing.Union["SearchRequest", typing.List["SearchRequest"]],
        *,
        model: oai_emb_model.OpenAIEmbeddingsModel,
        model_settings: oai_emb_model.ModelSettings,
    ) -> typing.List[typing.List[float]]:
        """
        Convert search requests to vector embeddings, handling various input types and encodings.

        This class method processes one or more SearchRequest objects, converting their queries
        into vector embeddings. It supports different input types (text, base64, or pre-computed vectors)
        and uses caching to improve performance for repeated queries.

        Parameters
        ----------
        search_requests : SearchRequest or List[SearchRequest]
            A single SearchRequest object or a list of SearchRequest objects to be processed.
        cache : Cache
            A diskcache.Cache object used for storing and retrieving cached embeddings.
        openai_client : openai.OpenAI
            An initialized OpenAI client object for making API calls to generate embeddings.

        Returns
        -------
        List[List[float]]
            A list of vector embeddings, where each embedding is a list of floats.
            The order of the output vectors corresponds to the order of the input search requests.

        Raises
        ------
        HTTPException
            If there's an error in processing any of the search requests, such as invalid encoding
            or mismatch between query type and encoding.

        Notes
        -----
        - The method handles three types of inputs:
        1. Text queries: Converted to embeddings using OpenAI's API (with caching).
        2. Base64 encoded vectors: Decoded to float vectors.
        3. Pre-computed float vectors: Used as-is.
        - For text queries, the method uses the `to_vectors_with_cache` function to generate
        and cache embeddings.
        - The method ensures that all output vectors have the correct dimensions as specified
        in the global settings.

        Examples
        --------
        >>> cache = Cache("./.cache/embeddings.cache")
        >>> openai_client = openai.OpenAI(api_key="your-api-key")
        >>> requests = [
        ...     SearchRequest(query="How does AI work?", top_k=5),
        ...     SearchRequest(query=[0.1, 0.2, 0.3, ...], top_k=3, encoding=EncodingType.VECTOR)
        ... ]
        >>> vectors = await SearchRequest.to_vectors(requests, cache=cache, openai_client=openai_client)
        >>> print(len(vectors), len(vectors[0]))
        2 512

        See Also
        --------
        to_vectors_with_cache : Function used for generating and caching text query embeddings.
        decode_base64_to_vector : Function used for decoding base64 encoded vectors.

        """  # noqa: E501

        search_requests = (
            [search_requests]
            if isinstance(search_requests, SearchRequest)
            else search_requests
        )

        output_vectors: typing.List[typing.Optional[typing.List[float]]] = [None] * len(
            search_requests
        )
        required_emb_items: collections.OrderedDict[int, typing.Text] = (
            collections.OrderedDict()
        )

        for idx, search_request in enumerate(search_requests):
            # Handle empty queries
            if not search_request.query:
                raise openai.BadRequestError(
                    message=f"Invalid queries[{idx}].",
                    response=dummy_httpx_response(400, b"Bad Request"),
                    body=None,
                )

            # Handle text queries
            if isinstance(search_request.query, typing.Text):
                # Query is hint for base64 encoding
                if search_request.encoding == EncodingType.BASE64:
                    output_vectors[idx] = TO.base64_to_vector(search_request.query)
                # Query is hint for vector, but query is not array, raise error
                elif search_request.encoding == EncodingType.VECTOR:
                    raise openai.BadRequestError(
                        message=(
                            f"Mismatch between queries[{idx}].encoding and "
                            + f"queries[{idx}].query."
                        ),
                        response=dummy_httpx_response(400, b"Bad Request"),
                        body=None,
                    )
                # Query is hint for plaintext, need to convert to vector
                elif search_request.encoding is EncodingType.PLAINTEXT:
                    required_emb_items[idx] = search_request.query
                # Query is provided as string, but no encoding hint
                else:
                    # Try to decode as base64 if string length is more than 12.
                    # If it can be decoded as base64, use it as a vector in high priority.  # noqa: E501
                    if (
                        IS.is_base64(search_request.query)
                        and len(search_request.query) > 12
                    ):
                        peek_query = (
                            f"{search_request.query[:12]}..."
                            if len(search_request.query) > 12
                            else search_request.query
                        )  # noqa: E501
                        logger.debug(
                            f"Probed `queries[{idx}].query='{peek_query}'` "
                            + "as base64 encoded."
                        )
                        output_vectors[idx] = TO.base64_to_vector(search_request.query)
                    else:
                        required_emb_items[idx] = search_request.query

            # Handle vectors
            else:
                output_vectors[idx] = search_request.query

        # Ensure all required embeddings are text
        if len(required_emb_items) > 0:
            embeddings_resp = model.get_embeddings(
                list(required_emb_items.values()),
                model_settings=model_settings,
            )
            for idx, embedding in zip(
                required_emb_items.keys(), embeddings_resp.to_python()
            ):
                output_vectors[idx] = embedding

        # Ensure all vectors are not None
        for idx, v in enumerate(output_vectors):
            assert v is not None, f"output_vectors[{idx}] is None"
            assert (
                len(v) == model_settings.dimensions
            ), f"output_vectors[{idx}] has wrong dimensions"
        return output_vectors  # type: ignore
