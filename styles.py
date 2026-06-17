css += """
    <style>
        section[data-testid="stSidebar"] {
            min-width: 240px !important;
            width: 240px !important;
        }
        section[data-testid="stSidebar"][aria-expanded="false"] {
            min-width: 0px !important;
            width: 0px !important;
        }
        [data-testid="collapsedControl"] {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            position: fixed !important;
            top: 10px !important;
            left: 10px !important;
            z-index: 999999 !important;
            background: #c9a84c !important;
            border-radius: 8px !important;
            padding: 4px !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4) !important;
        }
        [data-testid="collapsedControl"] svg {
            fill: #0a1628 !important;
            color: #0a1628 !important;
        }
        @media (max-width: 768px) {
            .main .block-container {
                padding: 1rem 0.5rem !important;
                max-width: 100% !important;
            }
        }
    </style>
    """
