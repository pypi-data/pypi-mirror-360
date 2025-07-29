import datetime
from typing import List, Optional

from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.prompts import PromptTemplate
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader,Document
from bs4 import BeautifulSoup

class RAGSystem:
    def __init__(self, index: VectorStoreIndex):
        self.index = index
        self.retriever = self.index.as_retriever(
            similarity_top_k=3
        )

        self.query_engine = self.index.as_query_engine(
            streaming=True,
            similarity_top_k=3,  # 限制参考片段数量
            response_mode="compact",  # 避免扩展无关内容
            node_postprocessors=[
                SimilarityPostprocessor(similarity_cutoff=0.5)  # 丢弃低分结果
            ]
        )
        qa_prompt = PromptTemplate("""
        [指令]
        你是一个严谨的知识库问答系统。请严格根据以下上下文回答问题。
        如果上下文明确包含答案，直接给出最简洁的回答（不超过1句话）。
        如果上下文不包含足够信息，只需回答"我不知道"。

        [上下文]
        {context_str}

        [问题]
        {query_str}

        [回答]
        """)

        self.query_engine.update_prompts({"response_synthesizer:text_qa_template": qa_prompt})

    def clean_text(text):
        # 移除HTML/广告等噪声
        soup = BeautifulSoup(text, "html.parser")
        for tag in soup(["footer", "script", "style"]):
            tag.decompose()
        return soup.get_text().strip()
    # 添加文档
    def add_documents(self, file_paths: List[str], scope: Optional[str] = None) -> List[str]:
        """添加文档到知识库
        Args:
            file_paths: 文档路径列表
            scope: 文档作用域/分类（会存入元数据）
        Returns:
            文档ID列表（格式为时间戳字符串）
        """
        # 获取现有文档的路径集合
        existing_paths = {
            doc["metadata"]["file_path"]
            for doc in self.list_documents()
            if "file_path" in doc["metadata"]
        }
        # 加载并过滤新文档
        documents = [
            doc for doc in SimpleDirectoryReader(input_files=file_paths).load_data()
            if doc.metadata["file_path"] not in existing_paths
        ]

        # 添加scope元数据
        for doc in documents:
            doc.metadata["scope"] = scope  # 关键行：仅添加scope字段

        # 插入非重复文档
        if documents:
            self.index.insert_nodes(documents)
            print(f"新增 {len(documents)} 个文档")
        else:
            print("所有文档均已存在，未添加新内容")
        return [doc.doc_id for doc in documents]

    # 删除文档
    def delete_document(self, doc_id: str) -> bool:
        """安全删除文档（同时清理docstore和ChromaDB）"""
        try:
            # 第一步：检查文档是否存在（通过ChromaDB直接查询）
            chroma_collection = self.index.vector_store._collection
            existing = chroma_collection.get(ids=[doc_id], include=[])
            if not existing["ids"]:
                print(f"文档 {doc_id} 不存在")
                return False

            # 2. 删除ChromaDB中的向量和元数据
            chroma_collection.delete(ids=[doc_id])

            # 3. 清理索引缓存（可选）
            if hasattr(self.index, '_storage_context'):
                self.index._storage_context.vector_store.delete(doc_id)

            print(f"成功删除文档 {doc_id}")
            return True

        except Exception as e:
            print(f"删除文档 {doc_id} 失败: {str(e)}")
            return False

    # 查询知识库
    def query(self, question: str, top_k: int = 5) -> str:
        """
            查询知识库并返回答案
            通过 严格检索约束+Prompt 设计+数据清洗 三管齐下，可基本消除幻觉回答。
        """

        # # 先单独运行检索检查
        # nodes = self.retriever.retrieve(question)
        # for node in nodes:
        #     print(f"相似度: {node.score:.2f} | 内容: {node.text[:100]}...")


        response = self.query_engine.query(question)
        # 逐块打印结果
        # full_response = []
        # 流式打印并收集内容
        for chunk in response.response_gen:
            print(chunk, end="", flush=True)
            # full_response.append(chunk)

        # 返回完整内容
        # return "".join(full_response)

    # 检索相关文档
    def retrieve_documents(self, query: str, top_k: int = 5) -> List[Document]:
        """检索与查询相关的文档"""
        nodes = self.retriever.retrieve(query)
        return [node.node for node in nodes[:top_k]]

    # 列出所有文档
    def list_documents(self,scope: Optional[str] = None) -> List[dict]:
        """列出知识库中的文档信息，可按scope筛选
        Args:
            scope: 筛选指定scope的文档（None表示不过滤）
        Returns:
            文档信息列表，每个文档包含id、metadata和text摘要
        """
        try:
            chroma_collection = self.index.vector_store._collection
            # 构造过滤条件（scope=None 时不过滤）
            where = {"scope": scope} if scope is not None else None
            # 直接通过元数据过滤查询
            collection_data = chroma_collection.get(
                where=where,  # 关键参数：按scope筛选
                include=["metadatas", "documents"]  # 只返回所需字段
            )

            return [{
                "id": doc_id,
                "metadata": metadata,
                "text": (text[:200] + "..." if len(text) > 200 else text)
            } for doc_id, text, metadata in zip(
                collection_data["ids"],
                collection_data["documents"],
                collection_data["metadatas"] or [{}] * len(collection_data["ids"])
            )]

        except Exception as e:
            print(f"获取文档列表时出错: {str(e)}")
            return []

    def _truncate_text(self, text: str, max_length: int = 50) -> str:
        """辅助函数：截断长文本"""
        return text[:max_length] + "..." if len(text) > max_length else text