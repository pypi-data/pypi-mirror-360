"""
Tests for annotation service.
"""
import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.annotation_service import AnnotationService
from services.vector_service import VectorService
from services.semantic_service import SemanticService
from services.llm_service import LLMService

class TestAnnotationService:
    """Test cases for AnnotationService."""
    
    @pytest.fixture
    def annotation_service(self):
        """Create annotation service instance for testing."""
        return AnnotationService()
    
    def test_annotation_service_initialization(self, annotation_service):
        """Test annotation service initialization."""
        assert annotation_service is not None
        assert isinstance(annotation_service.vector_service, VectorService)
        assert isinstance(annotation_service.semantic_service, SemanticService)
        assert isinstance(annotation_service.llm_service, LLMService)
    
    def test_extract_potential_entities(self, annotation_service):
        """Test potential entity extraction."""
        text = "我喜欢学习钢琴和绘画"
        entities = annotation_service._extract_potential_entities(text)
        
        assert isinstance(entities, list)
        assert "钢琴" in entities
        assert "绘画" in entities
    
    def test_annotate_text_basic(self, annotation_service):
        """Test basic text annotation."""
        text = "我喜欢钢琴"
        result = annotation_service.annotate_text(text, use_llm=False, use_vector=False)
        
        assert "text" in result
        assert "entities" in result
        assert "confidence" in result
        assert result["text"] == text
    
    def test_merge_entities(self, annotation_service):
        """Test entity merging functionality."""
        entities = [
            {"text": "钢琴", "confidence": 0.8, "source": "semantic"},
            {"text": "钢琴", "confidence": 0.9, "source": "llm"},
            {"text": "绘画", "confidence": 0.7, "source": "semantic"}
        ]
        
        merged = annotation_service._merge_entities(entities)
        
        assert len(merged) == 2
        # Should keep the higher confidence one
        piano_entity = next(e for e in merged if e["text"] == "钢琴")
        assert piano_entity["confidence"] == 0.9
    
    def test_calculate_overall_confidence(self, annotation_service):
        """Test overall confidence calculation."""
        result = {
            "entities": [
                {"confidence": 0.8},
                {"confidence": 0.9},
                {"confidence": 0.7}
            ],
            "methods_used": ["semantic", "llm"]
        }
        
        confidence = annotation_service._calculate_overall_confidence(result)
        
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.8  # Should be boosted by multiple methods
    
    def test_entities_to_bio_sequence(self, annotation_service):
        """Test BIO sequence generation."""
        text = "我喜欢钢琴"
        entities = [
            {"text": "钢琴", "label": "B-COURSE-钢琴"}
        ]
        
        tokens, labels = annotation_service._entities_to_bio_sequence(text, entities)
        
        assert len(tokens) == len(labels)
        assert len(tokens) == len(text)
        assert "B-COURSE-钢琴" in labels
        assert "I-COURSE-钢琴" in labels

class TestVectorService:
    """Test cases for VectorService."""
    
    @pytest.fixture
    def vector_service(self):
        """Create vector service instance for testing."""
        return VectorService()
    
    def test_vector_service_initialization(self, vector_service):
        """Test vector service initialization."""
        assert vector_service is not None
        assert vector_service.model_name is not None
        assert vector_service.dimension > 0
    
    def test_compute_similarity(self, vector_service):
        """Test similarity computation."""
        # Load model for testing
        vector_service.load_model()
        
        similarity = vector_service.compute_similarity("钢琴", "音乐")
        
        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.3  # Should have some similarity

class TestSemanticService:
    """Test cases for SemanticService."""
    
    @pytest.fixture
    def semantic_service(self):
        """Create semantic service instance for testing."""
        return SemanticService()
    
    def test_semantic_service_initialization(self, semantic_service):
        """Test semantic service initialization."""
        assert semantic_service is not None
        assert semantic_service.ontology_graph is not None
        assert len(semantic_service.course_hierarchy) > 0
    
    def test_get_entity_category(self, semantic_service):
        """Test entity category retrieval."""
        category = semantic_service.get_entity_category("钢琴")
        assert category == "乐器类"
        
        category = semantic_service.get_entity_category("篮球")
        assert category == "体育类"
    
    def test_get_related_entities(self, semantic_service):
        """Test related entity retrieval."""
        related = semantic_service.get_related_entities("钢琴", "siblings")
        
        assert isinstance(related, list)
        assert "小提琴" in related or "古筝" in related
    
    def test_infer_bio_label(self, semantic_service):
        """Test BIO label inference."""
        label = semantic_service.infer_bio_label("钢琴", "B")
        assert label == "B-COURSE-钢琴"
        
        label = semantic_service.infer_bio_label("钢琴", "I")
        assert label == "I-COURSE-钢琴"
    
    def test_string_similarity(self, semantic_service):
        """Test string similarity calculation."""
        similarity = semantic_service._string_similarity("钢琴", "钢琴")
        assert similarity == 1.0
        
        similarity = semantic_service._string_similarity("钢琴", "小提琴")
        assert 0.0 <= similarity <= 1.0

class TestLLMService:
    """Test cases for LLMService."""
    
    @pytest.fixture
    def llm_service(self):
        """Create LLM service instance for testing."""
        return LLMService()
    
    def test_llm_service_initialization(self, llm_service):
        """Test LLM service initialization."""
        assert llm_service is not None
        assert llm_service.bio_system_prompt is not None
    
    def test_fallback_annotation(self, llm_service):
        """Test fallback annotation when LLM is not available."""
        result = llm_service._fallback_annotation("我喜欢钢琴")
        
        assert "tokens" in result
        assert "labels" in result
        assert "entities" in result
        assert "confidence" in result
    
    def test_validate_annotation(self, llm_service):
        """Test annotation validation."""
        tokens = ["我", "喜", "欢", "钢", "琴"]
        labels = ["O", "O", "O", "B-COURSE-钢琴", "I-COURSE-钢琴"]
        
        validation = llm_service.validate_annotation(tokens, labels)
        
        assert "is_valid" in validation
        assert "issues" in validation
        assert "suggestions" in validation
        assert "total_entities" in validation
    
    def test_get_annotation_confidence(self, llm_service):
        """Test annotation confidence calculation."""
        annotation = {
            "entities": [
                {"text": "钢琴", "confidence": 0.9},
                {"text": "绘画", "confidence": 0.8}
            ]
        }
        
        confidence = llm_service.get_annotation_confidence("我喜欢钢琴和绘画", annotation)
        
        assert 0.0 <= confidence <= 1.0

# Integration tests
class TestIntegration:
    """Integration test cases."""
    
    def test_full_annotation_pipeline(self):
        """Test the complete annotation pipeline."""
        service = AnnotationService()
        text = "我喜欢学习钢琴和绘画"
        
        # Test without external dependencies
        result = service.annotate_text(text, use_llm=False, use_vector=False)
        
        assert result is not None
        assert "text" in result
        assert "entities" in result
        assert "confidence" in result
        assert len(result["entities"]) > 0

if __name__ == "__main__":
    pytest.main([__file__])

