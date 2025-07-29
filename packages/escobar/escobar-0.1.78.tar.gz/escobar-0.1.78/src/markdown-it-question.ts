// Simple markdown-it plugin for question blocks
export default function markdownItQuestion(md) {
    const defaultFence = md.renderer.rules.fence.bind(md.renderer.rules);
    md.renderer.rules.fence = (tokens, idx, options, env, self) => {
        const token = tokens[idx];
        if (token.info.trim() === 'question') {
            const content = token.content.trim();
            const lines = content.split('\n');
            const question = lines[0];
            const options = lines.slice(1).filter(line => line.trim());

            // Create the question block HTML
            let html = '<div class="escobar-question-block">';
            html += `<div class="escobar-question">${question}</div>`;
            html += '<div class="escobar-question-options">';

            // Add options with click handlers
            options.forEach((option, index) => {
                // Escape single quotes in the option text to prevent JS errors
                const escapedOption = option.replace(/'/g, "\\'");

                html += `<button class="escobar-question-option" data-option="${index}" 
                    onclick="(function() {
                        // Find the chat input textarea
                        const chatInput = document.querySelector('.escobar-chat-input');
                        if (chatInput) {
                            // Set the textarea value to the button text
                            chatInput.value = '${escapedOption}';
                            
                            // Find and click the send button
                            const sendButton = document.querySelector('.jp-Button.escobar-send-button');
                            if (sendButton) {
                                sendButton.click();
                            } else {
                                // Fallback to any button that might be the send button
                                const buttons = document.querySelectorAll('button');
                                for (const btn of buttons) {
                                    if (btn.textContent && ['Send', 'Talk', 'Plan', 'Act'].includes(btn.textContent.trim())) {
                                        btn.click();
                                        break;
                                    }
                                }
                            }
                        }
                    })();">${option}</button>`;
            });

            html += '</div></div>';
            return html;
        }
        return defaultFence(tokens, idx, options, env, self);
    };
}
