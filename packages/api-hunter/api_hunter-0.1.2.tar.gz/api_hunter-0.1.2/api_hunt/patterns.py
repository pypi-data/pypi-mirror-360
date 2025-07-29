API_KEY_PATTERNS = [
    # AWS
    r'AKIA[0-9A-Z]{16}',  # AWS Access Key
    r'[0-9a-zA-Z/+]{40}',  # AWS Secret Key (generic)

    # GitHub
    r'gh[opusr]_[0-9a-zA-Z]{36}',

    # Google
    r'AIza[0-9A-Za-z\-_]{35}',

    # Slack
    r'xox[boaprs]-[0-9]{12}-[0-9]{12}-[0-9a-zA-Z]{24}',

    # OpenAI
    r'sk-[a-zA-Z0-9]{48}',
    r'sk-proj-[a-zA-Z0-9]{48}',

    # Claude
    r'sk-ant-api03-[a-zA-Z0-9\-_]{95}',

    # Supabase
    r'eyJ[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+',
    r'sbp_[a-zA-Z0-9]{40}',

    # Generic
    r'["\']?[Aa]pi[_-]?[Kk]ey["\']?\s*[:=]\s*["\']?[0-9a-zA-Z_\-]{20,}["\']?',
    r'["\']?[Ss]ecret[_-]?[Kk]ey["\']?\s*[:=]\s*["\']?[0-9a-zA-Z_\-]{20,}["\']?',
    r'["\']?[Aa]ccess[_-]?[Tt]oken["\']?\s*[:=]\s*["\']?[0-9a-zA-Z_\-]{20,}["\']?',
    r'["\']?[Aa]uth[_-]?[Tt]oken["\']?\s*[:=]\s*["\']?[0-9a-zA-Z_\-]{20,}["\']?',
    r'Bearer\s+["\']?[a-zA-Z0-9_\-]{15,}["\']?',

    # URLs
    #r'[a-zA-Z][a-zA-Z0-9+.-]*://[^:@]+:[^@]+@[^/]+',

    # Private keys
    r'-----BEGIN (RSA|EC|DSA|OPENSSH|PGP )?PRIVATE KEY-----',

    # Stripe
    r'sk_live_[0-9a-zA-Z]{24}',
    r'sk_test_[0-9a-zA-Z]{24}',
    r'rk_live_[0-9a-zA-Z]{24}',
    r'rk_test_[0-9a-zA-Z]{24}',
    r'pk_live_[0-9a-zA-Z]{24}',
    r'pk_test_[0-9a-zA-Z]{24}',
    r'whsec_[0-9a-zA-Z]{32}',

    # Twilio
    r'SK[0-9a-fA-F]{32}',
    r'AC[0-9a-fA-F]{32}',

    # SendGrid
    r'SG\.[0-9a-zA-Z\-_]{22}\.[0-9a-zA-Z\-_]{43}',

    # Mailgun
    r'key-[0-9a-zA-Z]{32}',

    # Azure
    r'\b(?:[a-f0-9]{32}|[A-Za-z0-9+/=]{40,})\b'
    
    # DigitalOcean
    r'dop_v1_[0-9a-f]{64}',

    # Square
    r'sq0[a-z]{3}-[0-9a-zA-Z\-_]{22,43}',

    # Shopify
    r'shpat_[0-9a-fA-F]{32}',
    r'shpss_[0-9a-fA-F]{32}',
    r'shpca_[0-9a-fA-F]{32}',
    r'shppa_[0-9a-fA-F]{32}',

    # MongoDB Atlas
    r'mongodb\+srv:\/\/[^:\s]+:[^@\s]+@[^\/\s]+',


]

SCAN_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rb', '.php',
    '.cs', '.cpp', '.c', '.h', '.hpp', '.sh', '.bash', '.zsh', '.fish',
    '.yml', '.yaml', '.json', '.xml', '.env', '.config', '.conf', '.ini',
    '.txt', '.md', '.rst', '.sql', '.tf', '.tfvars'
}

IGNORE_PATTERNS = [
    r'\.git/',
    r'node_modules/',
    r'__pycache__/',
    r'\.pyc$',
    r'\.class$',
    r'\.o$',
    r'\.so$',
    r'\.dll$',
    r'\.exe$',
    r'\.bin$',
    r'\.lock$',
    r'package-lock\.json$',
    r'yarn\.lock$',
]
