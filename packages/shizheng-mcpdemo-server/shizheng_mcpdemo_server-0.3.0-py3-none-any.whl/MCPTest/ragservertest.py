import chromadb
import torch
from sentence_transformers import SentenceTransformer
import  os,sys
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Document,Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.storage import StorageContext
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from ragHandler import  RAGSystem


#基础路径
embeddingModelPath=r'/root/models/embedding/BAAI/bge-large-zh-v1.5' #embedding模型地址
llmPath=r'/root/models/Qwen1.5-0.5B-Chat' #本地大模型地址
chromadbPersistentPath = r"/root/pycharm/rag/chromadb"    #chroma持久化地址
chromaCollectionName = r"my_knowledge_base" #chroma集合名称
documentsPath = r"/root/pycharm/rag/documents"  #文档目录的路径


# 加载embedding模型
print(f"正在加载embedding模型:{embeddingModelPath}")
embed_model = HuggingFaceEmbedding(
    model_name=embeddingModelPath,device="cpu"
)

# 加载本地大模型
print(f"正在加载本地大模型:{embeddingModelPath}")
llm = HuggingFaceLLM(model_name=llmPath,
                    tokenizer_name=llmPath,
                     model_kwargs={
                         "trust_remote_code": True,
                         "attn_implementation": "flash_attention_2",  # 禁用sdpa，使用原始实现
                        "torch_dtype": torch.bfloat16,
                        "do_sample": False,  # 禁用随机性
                        "repetition_penalty": 1.5,  # 避免重复
                        # "max_new_tokens": 50,  # 限制生成长度
                     },
                     tokenizer_kwargs={"trust_remote_code": True}
            )
#指定全局模型
Settings.embed_model = embed_model
Settings.llm = llm
Settings.embed_metadata = False  # 禁止向量化元数据
Settings.llm_metadata_keys = []  # 禁止LLM看到元数据

# 初始化 ChromaDB（持久化）
print(f"正在初始化 ChromaDB")
chroma_client = chromadb.PersistentClient(chromadbPersistentPath)
try:
    chroma_collection = chroma_client.get_collection(chromaCollectionName)
    print(f"已加载集合:{chromaCollectionName} from {chromadbPersistentPath}")
except Exception as e:
    print(f"集合不存在，将创建新集合:{chromaCollectionName} to {chromadbPersistentPath}")
    chroma_collection = chroma_client.create_collection(chromaCollectionName,
                                        metadata={"hnsw:space": "cosine"})

print(f"正在初始化  VectorStoreIndex")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(
    vector_store=vector_store,
    docstore=None  # 显式禁用llamaindex的docstore
)
# 初始化VectorStoreIndex,  使用全局Settings中配置的embed_model
index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    storage_context=storage_context
)
print(f"初始化环境完毕！")

# 使用示例
if __name__ == "__main__":
    rag_system = RAGSystem(index)

    # # 1. 添加文档
    # sample_doc_path = os.path.join(documentsPath, "README_zh-CN.md")# 示例文档路径
    # print("\n--- 添加文档 ---")
    # doc_ids = rag_system.add_documents([sample_doc_path], scope="法律")
    # print(f"添加的文档ID: {doc_ids}")
#————————————————————————————————————————————————————————————————————————————————
    # 2. 列出所有文档
    print("\n--- 列出所有文档 ---")
    docs = rag_system.list_documents(scope="法律")
    for doc in docs:
        print(f"ID: {doc['id']}  file_name:{doc['metadata']['file_name']}  file_path: {doc['metadata']['file_path']} scope: {doc['metadata']['scope']}")
        #print(f"元数据: {doc['metadata']}")
        #print(f"内容摘要: {doc['text']}\n")
#————————————————————————————————————————————————————————————————————————————————
    # # 3. 查询知识库
    # print("\n--- 查询知识库 ---")
    # question = ".pt为扩展名的文件是什么?"
    # print(f"问题: {question}")
    # answer = rag_system.query(question)
    # print(f"最终回答: {answer}")
#————————————————————————————————————————————————————————————————————————————————
    # # 4. 检索相关文档
    # print("\n--- 检索相关文档 ---")
    # query = ".pt为扩展名的文件是什么?"
    # retrieved_docs = rag_system.retrieve_documents(query)
    # print(f"查询: {query}")
    # for i, doc in enumerate(retrieved_docs, 1):
    #     print(f"\n文档 {i}:")
    #     print(f"元数据: {doc.metadata}")
    #     print(f"内容摘要: {doc.text[:200]}...")
#————————————————————————————————————————————————————————————————————————————————


    # # 6. 删除文档
    # print("\n--- 删除文档 ---")
    # deleted = rag_system.delete_document("d3a4cfad-1127-4460-906d-c3259a3f7e04")
    # print(f"删除结果: {'成功' if deleted else '失败'}")