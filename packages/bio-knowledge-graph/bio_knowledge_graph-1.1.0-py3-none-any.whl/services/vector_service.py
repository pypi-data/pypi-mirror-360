"""
Vector service for semantic similarity and retrieval using local multilingual-e5-base model.
"""
import os
import pickle
import numpy as np
import faiss
from typing import List, Dict, Any, Tuple, Optional
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

class VectorService:
    """Vector service for semantic similarity and retrieval."""
    
    def __init__(self, model_path: str = None, dimension: int = 768):
        """
        Initialize vector service with local multilingual-e5-base model.
        
        Args:
            model_path: Path to local multilingual-e5-base model
            dimension: Vector dimension (768 for multilingual-e5-base)
        """
        # 设置本地模型路径
        self.model_path = model_path or os.getenv('LOCAL_MODEL_PATH', './models/multilingual-e5-base')
        self.model_name = "intfloat/multilingual-e5-base"
        self.dimension = dimension
        
        # 模型和索引
        self.model = None
        self.index = None
        self.metadata = []
        
        # 索引文件路径
        self.index_path = os.getenv('FAISS_INDEX_PATH', 'data/faiss_index.bin')
        self.metadata_path = os.getenv('METADATA_PATH', 'data/entity_metadata.pkl')
        
        # 确保数据目录存在
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        logger.info(f"VectorService initialized with local model path: {self.model_path}")
    
    def load_model(self) -> bool:
        """
        Load the local multilingual-e5-base model.
        
        Returns:
            bool: True if model loaded successfully
        """
        try:
            # 检查本地模型路径是否存在
            if os.path.exists(self.model_path):
                logger.info(f"Loading local model from: {self.model_path}")
                self.model = SentenceTransformer(self.model_path)
            else:
                # 如果本地路径不存在，尝试从缓存加载
                logger.warning(f"Local model path {self.model_path} not found, trying to load from cache")
                self.model = SentenceTransformer(self.model_name)
                
            # 验证模型维度
            test_embedding = self.model.encode("test", convert_to_tensor=False)
            actual_dimension = len(test_embedding)
            
            if actual_dimension != self.dimension:
                logger.warning(f"Model dimension mismatch: expected {self.dimension}, got {actual_dimension}")
                self.dimension = actual_dimension
            
            logger.info(f"Model loaded successfully. Dimension: {self.dimension}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def encode_text(self, text: str, normalize: bool = True) -> np.ndarray:
        """
        Encode text to vector using multilingual-e5-base model.
        
        Args:
            text: Input text
            normalize: Whether to normalize the vector
            
        Returns:
            np.ndarray: Text embedding vector
        """
        if self.model is None:
            if not self.load_model():
                raise RuntimeError("Failed to load model")
        
        try:
            # 为 E5 模型添加查询前缀
            if not text.startswith("query: "):
                text = f"query: {text}"
            
            # 编码文本
            embedding = self.model.encode(text, convert_to_tensor=False, normalize_embeddings=normalize)
            
            # 确保返回正确的维度
            if len(embedding) != self.dimension:
                logger.warning(f"Embedding dimension mismatch: expected {self.dimension}, got {len(embedding)}")
            
            return embedding.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Failed to encode text: {e}")
            raise
    
    def encode_batch(self, texts: List[str], normalize: bool = True, batch_size: int = 32) -> np.ndarray:
        """
        Encode multiple texts to vectors.
        
        Args:
            texts: List of input texts
            normalize: Whether to normalize vectors
            batch_size: Batch size for encoding
            
        Returns:
            np.ndarray: Array of embeddings
        """
        if self.model is None:
            if not self.load_model():
                raise RuntimeError("Failed to load model")
        
        try:
            # 为 E5 模型添加查询前缀
            processed_texts = []
            for text in texts:
                if not text.startswith("query: ") and not text.startswith("passage: "):
                    processed_texts.append(f"passage: {text}")
                else:
                    processed_texts.append(text)
            
            # 批量编码
            embeddings = self.model.encode(
                processed_texts, 
                convert_to_tensor=False, 
                normalize_embeddings=normalize,
                batch_size=batch_size,
                show_progress_bar=len(texts) > 100
            )
            
            return embeddings.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Failed to encode batch: {e}")
            raise
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            float: Cosine similarity score
        """
        try:
            # 编码文本
            embedding1 = self.encode_text(text1)
            embedding2 = self.encode_text(text2)
            
            # 计算余弦相似度
            similarity = np.dot(embedding1, embedding2) / (
                np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
            )
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Failed to compute similarity: {e}")
            return 0.0
    
    def build_index(self, texts: List[str], metadata: List[Dict] = None) -> bool:
        """
        Build FAISS index from texts.
        
        Args:
            texts: List of texts to index
            metadata: Optional metadata for each text
            
        Returns:
            bool: True if index built successfully
        """
        try:
            if not texts:
                logger.warning("No texts provided for indexing")
                return False
            
            logger.info(f"Building FAISS index for {len(texts)} texts...")
            
            # 编码所有文本
            embeddings = self.encode_batch(texts)
            
            # 创建 FAISS 索引
            self.index = faiss.IndexFlatIP(self.dimension)  # 使用内积索引
            
            # 添加向量到索引
            self.index.add(embeddings)
            
            # 保存元数据
            self.metadata = metadata or [{"text": text, "id": i} for i, text in enumerate(texts)]
            
            logger.info(f"FAISS index built successfully. Total vectors: {self.index.ntotal}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to build index: {e}")
            return False
    
    def add_to_index(self, texts: List[str], metadata: List[Dict] = None) -> bool:
        """
        Add new texts to existing index.
        
        Args:
            texts: List of texts to add
            metadata: Optional metadata for each text
            
        Returns:
            bool: True if texts added successfully
        """
        try:
            if self.index is None:
                logger.warning("No index exists, building new index")
                return self.build_index(texts, metadata)
            
            # 编码新文本
            embeddings = self.encode_batch(texts)
            
            # 添加到索引
            self.index.add(embeddings)
            
            # 添加元数据
            new_metadata = metadata or [{"text": text, "id": len(self.metadata) + i} for i, text in enumerate(texts)]
            self.metadata.extend(new_metadata)
            
            logger.info(f"Added {len(texts)} texts to index. Total vectors: {self.index.ntotal}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add to index: {e}")
            return False
    
    def search(self, query: str, k: int = 10, threshold: float = 0.5) -> List[Dict]:
        """
        Search for similar texts in the index.
        
        Args:
            query: Query text
            k: Number of results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List[Dict]: Search results with scores and metadata
        """
        try:
            if self.index is None:
                logger.warning("No index available for search")
                return []
            
            # 编码查询
            query_embedding = self.encode_text(query).reshape(1, -1)
            
            # 搜索
            scores, indices = self.index.search(query_embedding, k)
            
            # 处理结果
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0 and score >= threshold:
                    result = {
                        "score": float(score),
                        "index": int(idx),
                        "metadata": self.metadata[idx] if idx < len(self.metadata) else {}
                    }
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search: {e}")
            return []
    
    def find_similar(self, text: str, k: int = 5, exclude_self: bool = True) -> List[Dict]:
        """
        Find similar texts to the given text.
        
        Args:
            text: Input text
            k: Number of similar texts to return
            exclude_self: Whether to exclude the input text from results
            
        Returns:
            List[Dict]: Similar texts with similarity scores
        """
        try:
            results = self.search(text, k + (1 if exclude_self else 0))
            
            if exclude_self:
                # 过滤掉完全相同的文本
                filtered_results = []
                for result in results:
                    metadata = result.get("metadata", {})
                    if metadata.get("text", "") != text:
                        filtered_results.append(result)
                results = filtered_results[:k]
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to find similar texts: {e}")
            return []
    
    def cluster_texts(self, texts: List[str], n_clusters: int = None) -> Dict[str, Any]:
        """
        Cluster texts using K-means.
        
        Args:
            texts: List of texts to cluster
            n_clusters: Number of clusters (auto-determined if None)
            
        Returns:
            Dict: Clustering results
        """
        try:
            if not texts:
                return {"clusters": [], "labels": [], "centroids": []}
            
            # 编码文本
            embeddings = self.encode_batch(texts)
            
            # 确定聚类数量
            if n_clusters is None:
                n_clusters = min(10, max(2, len(texts) // 5))
            
            # K-means 聚类
            from sklearn.cluster import KMeans
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            labels = kmeans.fit_predict(embeddings)
            
            # 组织结果
            clusters = {}
            for i, label in enumerate(labels):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append({
                    "text": texts[i],
                    "index": i
                })
            
            return {
                "clusters": list(clusters.values()),
                "labels": labels.tolist(),
                "centroids": kmeans.cluster_centers_.tolist(),
                "n_clusters": n_clusters
            }
            
        except Exception as e:
            logger.error(f"Failed to cluster texts: {e}")
            return {"clusters": [], "labels": [], "centroids": []}
    
    def save_index(self, index_path: str = None, metadata_path: str = None) -> bool:
        """
        Save FAISS index and metadata to files.
        
        Args:
            index_path: Path to save index file
            metadata_path: Path to save metadata file
            
        Returns:
            bool: True if saved successfully
        """
        try:
            if self.index is None:
                logger.warning("No index to save")
                return False
            
            index_path = index_path or self.index_path
            metadata_path = metadata_path or self.metadata_path
            
            # 确保目录存在
            os.makedirs(os.path.dirname(index_path), exist_ok=True)
            os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
            
            # 保存索引
            faiss.write_index(self.index, index_path)
            
            # 保存元数据
            with open(metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
            
            logger.info(f"Index saved to {index_path}, metadata saved to {metadata_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
            return False
    
    def load_index(self, index_path: str = None, metadata_path: str = None) -> bool:
        """
        Load FAISS index and metadata from files.
        
        Args:
            index_path: Path to index file
            metadata_path: Path to metadata file
            
        Returns:
            bool: True if loaded successfully
        """
        try:
            index_path = index_path or self.index_path
            metadata_path = metadata_path or self.metadata_path
            
            if not os.path.exists(index_path) or not os.path.exists(metadata_path):
                logger.warning(f"Index files not found: {index_path}, {metadata_path}")
                return False
            
            # 加载索引
            self.index = faiss.read_index(index_path)
            
            # 加载元数据
            with open(metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
            
            logger.info(f"Index loaded from {index_path}, metadata loaded from {metadata_path}")
            logger.info(f"Index contains {self.index.ntotal} vectors")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get vector service statistics.
        
        Returns:
            Dict: Service statistics
        """
        stats = {
            "model_name": self.model_name,
            "model_path": self.model_path,
            "dimension": self.dimension,
            "model_loaded": self.model is not None,
            "index_available": self.index is not None,
            "total_vectors": self.index.ntotal if self.index else 0,
            "metadata_count": len(self.metadata),
            "index_path": self.index_path,
            "metadata_path": self.metadata_path
        }
        
        # 检查模型文件是否存在
        stats["local_model_exists"] = os.path.exists(self.model_path)
        
        # 检查索引文件是否存在
        stats["index_file_exists"] = os.path.exists(self.index_path)
        stats["metadata_file_exists"] = os.path.exists(self.metadata_path)
        
        return stats
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the vector service.
        
        Returns:
            Dict: Health check results
        """
        health = {
            "status": "healthy",
            "issues": []
        }
        
        try:
            # 检查模型
            if self.model is None:
                if not self.load_model():
                    health["status"] = "unhealthy"
                    health["issues"].append("Failed to load model")
            
            # 测试编码
            if self.model is not None:
                try:
                    test_embedding = self.encode_text("test")
                    if len(test_embedding) != self.dimension:
                        health["issues"].append(f"Dimension mismatch: {len(test_embedding)} != {self.dimension}")
                except Exception as e:
                    health["status"] = "unhealthy"
                    health["issues"].append(f"Encoding test failed: {e}")
            
            # 检查索引
            if self.index is None:
                health["issues"].append("No index available")
            
        except Exception as e:
            health["status"] = "unhealthy"
            health["issues"].append(f"Health check failed: {e}")
        
        return health

