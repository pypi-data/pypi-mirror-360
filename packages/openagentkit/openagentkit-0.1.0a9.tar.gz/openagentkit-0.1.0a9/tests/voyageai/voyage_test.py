from openagentkit.modules.voyageai import VoyageAIEmbeddingModel, AsyncVoyageAIEmbeddingModel, AsyncVoyageAIRerankerModel, VoyageAIRerankerModel
from scipy.spatial.distance import cosine
from sklearn.metrics.pairwise import cosine_similarity
import base64
import numpy as np
import asyncio

def k_nearest_neighbors(query_embedding, documents_embeddings, k=5):
    # Convert to numpy array
    query_embedding = np.array(query_embedding)
    documents_embeddings = np.array(documents_embeddings)

    # Reshape the query vector embedding to a matrix of shape (1, n) to make it 
    # compatible with cosine_similarity
    query_embedding = query_embedding.reshape(1, -1)

    # Calculate the similarity for each item in data
    cosine_sim = cosine_similarity(query_embedding, documents_embeddings)

    # Sort the data by similarity in descending order and take the top k items
    sorted_indices = np.argsort(cosine_sim[0])[::-1]

    # Take the top k related embeddings
    top_k_related_indices = sorted_indices[:k]
    top_k_related_embeddings = documents_embeddings[sorted_indices[:k]]
    top_k_related_embeddings = [
        list(row[:]) for row in top_k_related_embeddings
    ]  # convert to list

    return top_k_related_embeddings, top_k_related_indices

texts = [
    "The Mediterranean diet emphasizes fish, olive oil, and vegetables, believed to reduce chronic diseases.",
    "Photosynthesis in plants converts light energy into glucose and produces essential oxygen.",
    "20th-century innovations, from radios to smartphones, centered on electronic advancements.",
    "Rivers provide water, irrigation, and habitat for aquatic species, vital for ecosystems.",
    "Apple’s conference call to discuss fourth fiscal quarter results and business updates is scheduled for Thursday, November 2, 2023 at 2:00 p.m. PT / 5:00 p.m. ET.",
    "Shakespeare's works, like 'Hamlet' and 'A Midsummer Night's Dream,' endure in literature."
]

def test_voyageai_embedding_model():
    print("Testing VoyageAI Embedding Model...")
    b64_vo = VoyageAIEmbeddingModel(encoding_format="base64")
    vo = VoyageAIEmbeddingModel(encoding_format="float")

    b64_embeddings = b64_vo.encode_texts(texts)
    embeddings = vo.encode_texts(texts)

    for i, text in enumerate(texts):
        print(f"Text: {text}")
        decoded_bytes = base64.b64decode(b64_embeddings[i].embedding)
        decoded_array = np.frombuffer(decoded_bytes, dtype=np.float32).tolist()
        print(f"Cosine Similarity (Base64 vs Float): {1 - cosine(decoded_array, embeddings[i].embedding)}")

    query = "What is the Mediterranean diet?"

    query_embedding = vo.encode_query(query)
    print(f"Query: {query}")

    _, retrieved_embeddings_indices = k_nearest_neighbors(query_embedding.embedding, [e.embedding for e in embeddings], k=3)

    retrieved_docs = [texts[i] for i in retrieved_embeddings_indices]

    print("Top 3 retrieved documents:")
    for i, doc in enumerate(retrieved_docs):
        print(f"Document {i+1}: {doc}")

    reranker = VoyageAIRerankerModel()

    reranked_results = reranker.rerank(query, retrieved_docs, top_k=1)

    print("Reranked results:")
    for i, result in enumerate(reranked_results.results):
        print(f"Reranked Document {i+1}: {result.content} with score {result.relevance_score}")

async def test_async_voyageai_embedding_model():
    print("Testing Async VoyageAI Embedding Model...")
    b64_vo = AsyncVoyageAIEmbeddingModel(encoding_format="base64")
    vo = AsyncVoyageAIEmbeddingModel(encoding_format="float")

    b64_embeddings = await b64_vo.encode_texts(texts)
    embeddings = await vo.encode_texts(texts)

    for i, text in enumerate(texts):
        print(f"Text: {text}")
        decoded_bytes = base64.b64decode(b64_embeddings[i].embedding)
        decoded_array = np.frombuffer(decoded_bytes, dtype=np.float32).tolist()
        print(f"Cosine Similarity (Base64 vs Float): {1 - cosine(decoded_array, embeddings[i].embedding)}")

    query = "What is the Mediterranean diet?"

    query_embedding = await vo.encode_query(query)
    print(f"Query: {query}")

    _, retrieved_embeddings_indices = k_nearest_neighbors(query_embedding.embedding, [e.embedding for e in embeddings], k=3)

    retrieved_docs = [texts[i] for i in retrieved_embeddings_indices]

    print("Top 3 retrieved documents:")
    for i, doc in enumerate(retrieved_docs):
        print(f"Document {i+1}: {doc}")

    reranker = AsyncVoyageAIRerankerModel()

    reranked_results = await reranker.rerank(query, retrieved_docs, top_k=1)

    print("Reranked results:")
    for i, result in enumerate(reranked_results.results):
        print(f"Reranked Document {i+1}: {result.content} with score {result.relevance_score}")

if __name__ == "__main__":
    test_voyageai_embedding_model()
    # Uncomment the following line to test the async function
    # asyncio.run(test_async_voyageai_embedding_model())