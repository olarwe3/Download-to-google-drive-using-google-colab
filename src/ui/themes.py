"""
Theme and styling utilities for the UI components
"""
from ..utils.constants import UI_THEMES

def get_adaptive_css() -> str:
    """Get adaptive CSS that works with both light and dark themes"""
    return """
    <style>
    /* Adaptive theme styles for Colab compatibility */
    .dm-container {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        max-width: 100%;
        margin: 0;
        background: var(--colab-primary-surface-color, #fff);
        border: 1px solid var(--colab-border-color, #e1e5e9);
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        color: var(--colab-primary-text-color, #000);
    }
    
    .dm-header {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        padding: 16px 20px;
        text-align: center;
        position: relative;
    }
    
    .dm-title {
        font-size: 20px;
        font-weight: 600;
        margin: 0 0 4px 0;
        line-height: 1.2;
        color: white !important;
    }
    
    .dm-subtitle {
        font-size: 13px;
        opacity: 0.9;
        margin: 0;
        font-weight: 400;
        color: white !important;
    }
    
    .dm-status {
        position: absolute;
        top: 16px;
        right: 20px;
        display: flex;
        align-items: center;
        font-size: 12px;
        color: white !important;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 6px;
    }
    
    .status-good { background: #10b981; }
    .status-warning { background: #f59e0b; }
    .status-error { background: #ef4444; }
    
    .dm-content {
        padding: 0;
        background: var(--colab-primary-surface-color, #fff);
        color: var(--colab-primary-text-color, #000);
    }
    
    .quick-section {
        padding: 16px 20px;
        border-bottom: 1px solid var(--colab-border-color, #f3f4f6);
        background: var(--colab-secondary-surface-color, #f9fafb);
    }
    
    .quick-title {
        font-size: 14px;
        font-weight: 600;
        color: var(--colab-primary-text-color, #374151);
        margin: 0 0 12px 0;
    }
    
    .tab-content {
        padding: 16px 20px;
        background: var(--colab-primary-surface-color, #fff);
        color: var(--colab-primary-text-color, #000);
    }

    /* Widget theme compatibility */
    .widget-tab > .widget-tab-contents {
        background: var(--colab-primary-surface-color, #fff) !important;
        color: var(--colab-primary-text-color, #000) !important;
    }
    
    .widget-tab > .tab-content {
        background: var(--colab-primary-surface-color, #fff) !important;
        color: var(--colab-primary-text-color, #000) !important;
    }

    /* Tab styling */
    .p-TabBar-tab {
        background: var(--colab-primary-surface-color, #fff) !important;
        color: var(--colab-primary-text-color, #000) !important;
        border-bottom: 2px solid transparent !important;
    }
    
    .p-TabBar-tab:hover {
        background: var(--colab-secondary-surface-color, #f5f5f5) !important;
    }
    
    .p-TabBar-tab.p-mod-current {
        background: var(--colab-primary-surface-color, #fff) !important;
        color: var(--colab-primary-text-color, #000) !important;
        border-bottom: 2px solid #4f46e5 !important;
    }
    
    .p-TabBar-tabLabel {
        color: var(--colab-primary-text-color, #000) !important;
    }

    /* Widget styling improvements */
    .widget-vbox, .widget-hbox {
        background: var(--colab-primary-surface-color, #fff) !important;
        color: var(--colab-primary-text-color, #000) !important;
    }

    .widget-text, .widget-textarea {
        background: var(--colab-primary-surface-color, #fff) !important;
        color: var(--colab-primary-text-color, #000) !important;
        border: 1px solid var(--colab-border-color, #ccc) !important;
    }

    .widget-dropdown {
        background: var(--colab-primary-surface-color, #fff) !important;
        color: var(--colab-primary-text-color, #000) !important;
    }

    .widget-label {
        color: var(--colab-primary-text-color, #000) !important;
    }

    .widget-html {
        color: var(--colab-primary-text-color, #000) !important;
    }

    .output_area {
        background: var(--colab-primary-surface-color, #fff) !important;
        color: var(--colab-primary-text-color, #000) !important;
    }

    /* Dark mode overrides */
    @media (prefers-color-scheme: dark) {
        .dm-container {
            background: #1f2937 !important;
            border-color: #374151 !important;
            color: #f9fafb !important;
        }
        
        .dm-content {
            background: #1f2937 !important;
            color: #f9fafb !important;
        }
        
        .quick-section {
            background: #111827 !important;
            border-color: #374151 !important;
        }
        
        .quick-title {
            color: #f9fafb !important;
        }
        
        .p-TabBar-tab {
            background: #1f2937 !important;
            color: #f9fafb !important;
        }
        
        .p-TabBar-tab:hover {
            background: #374151 !important;
        }
        
        .p-TabBar-tab.p-mod-current {
            background: #1f2937 !important;
            color: #f9fafb !important;
        }
        
        .p-TabBar-tabLabel {
            color: #f9fafb !important;
        }
        
        .widget-tab > .widget-tab-contents {
            background: #1f2937 !important;
            color: #f9fafb !important;
        }
        
        .widget-tab > .tab-content {
            background: #1f2937 !important;
            color: #f9fafb !important;
        }
        
        .widget-vbox, .widget-hbox {
            background: #1f2937 !important;
            color: #f9fafb !important;
        }

        .widget-text, .widget-textarea {
            background: #374151 !important;
            color: #f9fafb !important;
            border: 1px solid #6b7280 !important;
        }

        .widget-dropdown {
            background: #374151 !important;
            color: #f9fafb !important;
        }

        .widget-label {
            color: #f9fafb !important;
        }

        .widget-html {
            color: #f9fafb !important;
        }

        .output_area {
            background: #1f2937 !important;
            color: #f9fafb !important;
        }
    }
    
    /* Progress bar styling */
    .widget-progress {
        background: var(--colab-secondary-surface-color, #f0f0f0) !important;
    }
    
    .widget-progress .progress-bar {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
    }
    
    /* Button styling */
    .widget-button {
        border-radius: 6px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    
    .widget-button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }
    
    /* Info boxes */
    .info-box {
        background: var(--colab-secondary-surface-color, #f8fafc);
        border: 1px solid var(--colab-border-color, #e2e8f0);
        border-radius: 8px;
        padding: 12px 16px;
        margin: 8px 0;
        color: var(--colab-primary-text-color, #334155);
    }
    
    .info-box.success {
        background: #f0fdf4;
        border-color: #bbf7d0;
        color: #166534;
    }
    
    .info-box.warning {
        background: #fffbeb;
        border-color: #fed7aa;
        color: #92400e;
    }
    
    .info-box.error {
        background: #fef2f2;
        border-color: #fecaca;
        color: #dc2626;
    }
    
    @media (prefers-color-scheme: dark) {
        .info-box {
            background: #1e293b;
            border-color: #334155;
            color: #cbd5e1;
        }
        
        .info-box.success {
            background: #064e3b;
            border-color: #065f46;
            color: #6ee7b7;
        }
        
        .info-box.warning {
            background: #78350f;
            border-color: #92400e;
            color: #fbbf24;
        }
        
        .info-box.error {
            background: #7f1d1d;
            border-color: #991b1b;
            color: #fca5a5;
        }
    }
    </style>
    """

def get_speed_tips_html() -> str:
    """Get HTML for speed optimization tips"""
    return """
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 15px; border-radius: 10px; margin: 10px 0; color: white;">
        <h4 style="margin: 0 0 10px 0; color: white;">🚀 Speed Optimization Features</h4>
        <ul style="margin: 5px 0; padding-left: 20px;">
            <li><strong>Segmented Downloads:</strong> Use for files >10MB to split into multiple parallel connections</li>
            <li><strong>Chunk Size:</strong> Now using 256KB chunks (32x larger) for better performance</li>
            <li><strong>Concurrent Downloads:</strong> Increase to 8-10 for batch downloads if you have good internet</li>
            <li><strong>Connection Reuse:</strong> Sessions are now reused for better TCP performance</li>
            <li><strong>Server Headers:</strong> Optimized headers improve compatibility and reduce delays</li>
        </ul>
        <p style="margin: 10px 0 0 0; font-size: 12px; opacity: 0.9;">
            💡 Expected improvement: 3-5x faster downloads compared to previous version
        </p>
    </div>
    """

def get_error_display_html(title: str, message: str, steps: list = None) -> str:
    """Generate HTML for error display with steps"""
    steps_html = ""
    if steps:
        steps_html = "<div style='background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px; margin: 20px 0;'>"
        steps_html += "<p><strong>📋 Required Steps:</strong></p>"
        for i, step in enumerate(steps, 1):
            steps_html += f"<p>{i}. {step}</p>"
        steps_html += "</div>"
    
    return f"""
    <div style="background: linear-gradient(135deg, #ff6b6b, #ee5a24); 
                padding: 30px; border-radius: 15px; text-align: center; 
                color: white; margin: 20px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
        <h2>⚠️ {title}</h2>
        <p style="font-size: 18px; margin: 20px 0;">{message}</p>
        {steps_html}
    </div>
    """

def get_success_display_html(title: str, message: str, features: list = None) -> str:
    """Generate HTML for success display with features"""
    features_html = ""
    if features:
        features_html = "<ul style='text-align: left; margin: 20px 0; padding-left: 20px;'>"
        for feature in features:
            features_html += f"<li>{feature}</li>"
        features_html += "</ul>"
    
    return f"""
    <div style="background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%); 
                padding: 20px; border-radius: 15px; text-align: center; 
                color: white; margin: 10px 0; box-shadow: 0 4px 20px rgba(0,0,0,0.2);">
        <h3>🎉 {title}</h3>
        <p style="font-size: 16px; margin: 15px 0;">{message}</p>
        {features_html}
    </div>
    """

def get_theme_adaptation_script() -> str:
    """Get JavaScript for theme adaptation"""
    return """
    <script>
    // Function to apply theme-aware styling to tabs and widgets
    function applyThemeToInterface() {
        // Get the current theme (detect if we're in dark mode)
        const isDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        const colabIsDark = document.querySelector('.notebook-container') &&
                           (document.querySelector('.notebook-container').classList.contains('theme-dark') ||
                            document.body.classList.contains('theme-dark') ||
                            getComputedStyle(document.body).backgroundColor === 'rgb(31, 41, 55)');

        const darkTheme = isDarkMode || colabIsDark;

        // Apply appropriate styling based on theme
        const textColor = darkTheme ? '#f9fafb' : '#000';
        const bgColor = darkTheme ? '#1f2937' : '#fff';
        const inputBgColor = darkTheme ? '#374151' : '#fff';
        const borderColor = darkTheme ? '#6b7280' : '#ccc';

        // Style tab elements
        const tabs = document.querySelectorAll('.p-TabBar-tab, .widget-tab .tab-content');
        const tabLabels = document.querySelectorAll('.p-TabBar-tabLabel');
        const tabContents = document.querySelectorAll('.widget-tab-contents, .tab-content');

        tabs.forEach(tab => {
            tab.style.color = textColor + ' !important';
            tab.style.backgroundColor = bgColor + ' !important';
            tab.style.borderColor = borderColor + ' !important';
        });

        tabLabels.forEach(label => {
            label.style.color = textColor + ' !important';
        });

        tabContents.forEach(content => {
            content.style.backgroundColor = bgColor + ' !important';
            content.style.color = textColor + ' !important';
        });

        // Style widget elements
        const widgets = document.querySelectorAll('.widget-vbox, .widget-hbox');
        const inputs = document.querySelectorAll('.widget-text input, .widget-textarea textarea, .widget-dropdown select');
        const labels = document.querySelectorAll('.widget-label');
        const htmlElements = document.querySelectorAll('.widget-html');
        const outputs = document.querySelectorAll('.output_area');

        widgets.forEach(widget => {
            widget.style.backgroundColor = bgColor + ' !important';
            widget.style.color = textColor + ' !important';
        });

        inputs.forEach(input => {
            input.style.backgroundColor = inputBgColor + ' !important';
            input.style.color = textColor + ' !important';
            input.style.borderColor = borderColor + ' !important';
        });

        labels.forEach(label => {
            label.style.color = textColor + ' !important';
        });

        htmlElements.forEach(html => {
            html.style.color = textColor + ' !important';
        });

        outputs.forEach(output => {
            output.style.backgroundColor = bgColor + ' !important';
            output.style.color = textColor + ' !important';
        });

        console.log('Theme applied:', darkTheme ? 'dark' : 'light');
    }

    // Apply styling immediately
    setTimeout(applyThemeToInterface, 200);

    // Reapply when theme changes
    if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applyThemeToInterface);
    }

    // Also reapply periodically to catch any dynamic changes
    setInterval(applyThemeToInterface, 3000);
    </script>
    """
