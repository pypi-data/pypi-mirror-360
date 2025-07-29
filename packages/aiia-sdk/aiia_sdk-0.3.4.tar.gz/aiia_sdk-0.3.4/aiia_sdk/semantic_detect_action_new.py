def semantic_detect_action(self, output_text: str) -> Optional[str]:
    """Detect action type from AI output using semantic similarity or keyword fallback."""
    if not output_text or not isinstance(output_text, str):
        return None
        
    try:
        # 1. Check for manual override rules first
        override_code = self._apply_override_rules(output_text)
        if override_code:
            self.log_action(
                override_code, 
                context={
                    "output": output_text[:200],
                    "detection_method": "override_rule"
                }, 
                registered=True
            )
            return override_code

        # 2. Check if semantic detection is available
        if not _HAS_SEMANTIC_DEPS:
            return self._fallback_to_keyword_detection(output_text, 
                                                     reason="Semantic dependencies not available")
        
        if self.semantic_model is None:
            return self._fallback_to_keyword_detection(output_text, 
                                                     reason="Semantic model not loaded")
        
        if not self.semantic_embeddings:
            return self._fallback_to_keyword_detection(output_text, 
                                                     reason="No semantic action embeddings")
            
        # 3. Try semantic detection
        try:
            from .semantic_singleton import SemanticModelSingleton
            import numpy as np
            
            # Get embedding for output text
            output_embedding = SemanticModelSingleton.get_embedding(output_text)
            
            # Check if embedding is None explicitly
            if output_embedding is None:
                return self._fallback_to_keyword_detection(output_text, 
                                                         reason="Could not generate text embedding")
            
            # Ensure output_embedding is a NumPy array and 1D
            if hasattr(output_embedding, 'cpu') and hasattr(output_embedding, 'numpy'):
                # Convert PyTorch tensor to NumPy
                output_embedding = output_embedding.cpu().numpy()
            
            # Ensure it's a NumPy array
            if not isinstance(output_embedding, np.ndarray):
                output_embedding = np.array(output_embedding)
                
            # Ensure it's 1D
            output_embedding = np.squeeze(output_embedding)
            
            # Initialize variables for tracking best match
            best_score = -1.0  # Use float to avoid any array comparison issues
            best_index = -1
            
            # Calculate similarity with each action
            for i, action_embedding in enumerate(self.semantic_embeddings):
                # Process action embedding
                if hasattr(action_embedding, 'cpu') and hasattr(action_embedding, 'numpy'):
                    action_embedding = action_embedding.cpu().numpy()
                
                if not isinstance(action_embedding, np.ndarray):
                    action_embedding = np.array(action_embedding)
                    
                action_embedding = np.squeeze(action_embedding)
                
                # Calculate cosine similarity manually and safely
                # Convert all intermediate results to Python scalars to avoid array comparisons
                dot_product = float(np.sum(output_embedding * action_embedding))
                norm_output = float(np.sqrt(np.sum(output_embedding * output_embedding)))
                norm_action = float(np.sqrt(np.sum(action_embedding * action_embedding)))
                
                # Avoid division by zero
                if norm_output > 0.0 and norm_action > 0.0:
                    similarity = dot_product / (norm_output * norm_action)
                    
                    # Use explicit float comparison
                    if float(similarity) > best_score:
                        best_score = float(similarity)
                        best_index = i
            
            # Apply confidence threshold with explicit float comparison
            threshold = 0.5
            if best_score > threshold and best_index >= 0:
                action_code = self.semantic_actions[best_index]["code"]
                
                self.log_action(
                    action_code, 
                    context={
                        "output": output_text[:200],
                        "confidence": float(best_score),
                        "detection_method": "semantic"
                    },
                    registered=True
                )
                return action_code
                
            # If confidence is below threshold, try keyword fallback
            fallback_code = self._keyword_based_detection(output_text)
            if fallback_code:
                self.log_action(
                    fallback_code,
                    context={
                        "output": output_text[:200],
                        "detection_method": "keyword_fallback",
                        "semantic_confidence": float(best_score),
                        "note": "Below confidence threshold"
                    },
                    registered=True
                )
                return fallback_code
            
            # If all else fails, return UNKNOWN
            self.log_action(
                "UNKNOWN",
                context={
                    "output": output_text[:200],
                    "semantic_confidence": float(best_score),
                    "note": "No semantic or keyword match found"
                },
                registered=True
            )
            return "UNKNOWN"
            
        except Exception as e:
            print(f"[AIIA SDK] ⚠️ Error in semantic detection: {e}")
            return self._fallback_to_keyword_detection(output_text, 
                                                      reason=f"Semantic error: {str(e)[:100]}")
            
    except Exception as e:
        print(f"[AIIA SDK] ⚠️ Error in action detection: {e}")
        try:
            fallback_code = self._keyword_based_detection(output_text) or "UNKNOWN"
            self.log_action(
                fallback_code,
                context={
                    "output": output_text[:200],
                    "detection_method": "emergency_fallback",
                    "error": str(e)[:100]
                },
                registered=True
            )
            return fallback_code
        except Exception:
            self.log_action(
                "UNKNOWN",
                context={
                    "output": output_text[:200] if output_text else "None",
                    "note": "Critical error in action detection"
                },
                registered=True
            )
            return "UNKNOWN"
