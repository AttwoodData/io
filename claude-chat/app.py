<!-- Chat Container -->
        <div class="chat-container">
            <!-- Model Selector -->
            <div class="model-selector">
                <div class="model-selector-header">
                    <span>Choose AI Model:</span>
                </div>
                <div class="model-options">
                    <label class="model-option">
                        <input type="radio" name="llm-model" value="local-general" 
                               id="radio-local-general" checked>
                        <div class="model-info">
                            <span class="model-name">🖥️ Local (Qwen2.5 14B)</span>
                            <span class="model-desc">Free • General Purpose</span>
                        </div>
                    </label>
                    
                    <label class="model-option">
                        <input type="radio" name="llm-model" value="local-coder" 
                               id="radio-local-coder">
                        <div class="model-info">
                            <span class="model-name">💻 Local Coder (Qwen2.5)</span>
                            <span class="model-desc">Free • Code Optimized</span>
                        </div>
                    </label>
                    
                    <label class="model-option">
                        <input type="radio" name="llm-model" value="claude" 
                               id="radio-claude">
                        <div class="model-info">
                            <span class="model-name">⚡ Claude Sonnet 4.5</span>
                            <span class="model-desc">Premium • Best Quality</span>
                        </div>
                    </label>
                </div>
            </div>
            
            <!-- Model Indicator -->
            <div class="model-indicator" id="model-indicator">
                <span class="indicator-label">Active:</span>
                <span class="indicator-value" id="current-model">Local (Qwen2.5 14B)</span>
                <span class="indicator-stats" id="model-stats"></span>
            </div>
            
            <!-- Messages Display -->