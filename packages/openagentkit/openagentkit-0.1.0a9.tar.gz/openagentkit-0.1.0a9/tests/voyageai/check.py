from openagentkit.modules.voyageai import VoyageAIEmbeddingModel
from scipy.spatial.distance import cosine

b64_vo = VoyageAIEmbeddingModel(encoding_format="float")

textA = """
Bangkok Bank M VISA Credit Card X Mattress Promotion
Content: Additional 5% discount on beds and bedding products for full payments of 5,000 Baht or more. Maximum discount of 5,000 Baht per receipt.
Conditions: This on-top discount cannot be combined with M Cash redemption or the use of reward points to receive special discounts other than the 12.5% discount available with other Bangkok Bank M privileges. Cashiers must inform customers that no other promotions can be applied before processing the payment. Customers must activate the privilege to display the redemption code and show the secret code to the cashier [CODE: MATBBLM]. The cashier must record the redemption code shown on the M Card App along with the purchase amount after the discount in the Log Sheet as proof for the bank.
Mall supported: MLIFESTORE, KORAT, EMQUARTIER, PARAGON
Credit card supported: BBLM
Start date: March 1, 2025
End date: June 30, 2025
""".strip()

textB = """
Bangkok Bank M VISA X Mattress Credit Card Promotion
Content: Exclusive offers for Bangkok Bank M VISA credit cardholders shopping for mattresses.
Conditions: Conditions and further offer details are to be provided by the respective departments.
Mall supported: MLIFESTORE, KORAT, EMQUARTIER, PARAGON
Credit card supported: BBLM
Start date: March 1, 2025
End date: June 30, 2025
""".strip()

def test_voyageai_embedding_model():
    print("Testing VoyageAI Embedding Model...")
    
    b64_embeddings = b64_vo.encode_texts([textA, textB], include_metadata=False)

    embeddingA = b64_embeddings[0].embedding
    embeddingB = b64_embeddings[1].embedding

    # Calculate cosine similarity between the two embeddings
    co = cosine(embeddingA, embeddingB)
    print(f"Cosine Distance: {co}")
    print(f"Cosine Similarity (1 - Cosine Distance): {1 - co}")

if __name__ == "__main__":
    test_voyageai_embedding_model()