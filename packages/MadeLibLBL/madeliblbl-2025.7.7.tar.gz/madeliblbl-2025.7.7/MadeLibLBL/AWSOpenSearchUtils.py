from .AWSBedrockUtils import generate_embeddings

def retrieve_rerank_context_from_opensearch(opensearch_client, opensearch_index_name: str, embed_model, rerank_model, query: str, k: int = 15, top_n: int = 5, model_id: str="cohere.rerank-v3-5:0") -> str:
    """Retrieves and reranks relevant documents from OpenSearch using vector search and semantic reranking.

    Performs a two-phase retrieval process:
    1. Vector similarity search in OpenSearch to find initial candidates
    2. Semantic reranking of results using Cohere's rerank model

    Args:
        opensearch_client: Authenticated OpenSearch client
        opensearch_index_name: Name of the OpenSearch index containing documents
        embed_model: Text embedding model (must implement get_text_embedding())
        rerank_model: Cohere rerank model instance
        query: Search query string
        k: Number of initial documents to retrieve (default: 15)
        top_n: Number of top documents to return after reranking (default: 5)
        model_id: Identifier of the Cohere rerank model (default: "cohere.rerank-v3-5:0")

    Returns:
        str: Formatted string containing the top_n most relevant documents with their metadata,
             or empty string if an error occurs

    Raises:
        Exception: Logs any errors during the retrieval process

    Example:
        >>> context = retrieve_rerank_context_from_opensearch(
                os_client,
                "knowledge-base",
                embed_model,
                rerank_model,
                "What is machine learning?",
                k=10,
                top_n=3
            )
        >>> print(context)
        Source: ml_intro.pdf
        Content: Machine learning is a subset of AI...
        Source: ai_basics.docx
        Content: ML algorithms learn patterns from data...
    """
    try:
        # Generate embedding for the query
        query_embedding = generate_embeddings(embed_model, query)
        
        # Vector search query
        search_body = {
            "size": k,
            "query": {
                "knn": {
                    "vector": {
                        "vector": query_embedding,
                        "k": k
                    }
                }
            }
        }
        
        retrieval_response = opensearch_client.search(
            index=opensearch_index_name,
            body=search_body
        )
        
        # Process and concatenate results
        contexts = []
        for hit in retrieval_response['hits']['hits']:
            content = hit['_source']['content']
            filename = hit['_source']['filename']
            contexts.append(f"Fonte: {filename}\nConteúdo: {content}\n")
        
        rerank_response = rerank_model.rerank(
            model=model_id,
            query=query,
            documents=contexts,
            top_n=top_n,
        )
        
        # Extract the reranked documents indexes
        rerank_response_index = [result_index.index for result_index in rerank_response.results]
        
        # Select the reranked documents using the rerank_response_index
        reranked_contexts = [contexts[index] for index in rerank_response_index]

        # Join the reranked contexts into a single string
        reranked_results = "\n".join(reranked_contexts)

        return reranked_results
    
    except Exception as e:
        print(f"Error retrieving context from OpenSearch: {str(e)}")