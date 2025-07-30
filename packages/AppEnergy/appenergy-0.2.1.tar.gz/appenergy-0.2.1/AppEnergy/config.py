"""
Configuration and constants for the App Category Analyzer.
"""

# Headers for Snapcraft API
SNAP_HEADERS = {
    "Snap-Device-Series": "16",
    "User-Agent": "SnapInfoCLI/1.0",
    "Accept": "application/json"
}

# General headers for other requests
GENERAL_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

# Predefined main categories
# Predefined main and sub categories
MAIN_CATEGORIES = {
    "internet_browsers": ["chrome", "firefox", "safari", "edge", "opera", "browser", "web", "internet"],
    "productivity_tools": ["office", "calendar", "spreadsheet", "presentation", "productivity", "document", "editor", "notes"],
    "communication_collaboration": ["messenger", "chat", "email", "communication", "collaboration", "meeting", "video conference", "social"],
    "out_of_browser_entertainment": ["facebook", "instagram", "game", "entertainment", "media", "player", "streaming", "video"],
    "utilities_maintenance": ["utility", "maintenance", "system", "cleaner", "optimizer", "security", "antivirus", "backup"],
    "media_creation": ["graphic", "design", "video", "editing", "photo", "media", "creation", "audio", "music", "recording"],
    "development_programming": ["ide", "version", "control", "development", "programming", "coding", "compiler", "debugger", "git"],
    "others": ["specialized", "accessibility", "virtualization", "health", "research", "iot", "cryptocurrency"]
}

CATEGORIES = {
    "internet_browsers": {
        "chrome", "firefox", "safari", "edge", "opera", "brave", "vivaldi", "tor","adblocker", "password_manager", "vpn", "translator", "screenshot",
        "download", "accelerator", "torrent", "file_transfer",
        "rss", "atom", "news_aggregator", "content_reader",
        "inspector", "web_debugging", "site_analyzer", "lighthouse"
    },
    
    "productivity_tools": {
        "microsoft_office", "libreoffice", "openoffice", "wps_office", "google_workspace",
        "word_processor", "text_editor", "markdown", "pdf", "note_taking",
        "excel", "calc", "data_analysis", "formula", "charts",
        "powerpoint", "slides", "presentation_maker", "keynote",
        "todo", "kanban", "project_management", "time_tracking", "pomodoro",
       "evernote", "onenote", "notion", "joplin", "sticky_notes",
       "calendar", "appointment", "reminder", "scheduling", "planner"
    },
    
    "communication_collaboration": {
       "messenger", "whatsapp", "signal", "telegram", "wechat", "viber",
      "mail", "email_manager", "gmail", "outlook", "thunderbird",
        "zoom", "webex", "skype", "meet", "teams", "video_call",
       "slack", "discord", "mattermost", "group_editor", "real_time_collab",
      "social", "network", "twitter", "instagram", "linkedin",
        "voip", "voice_chat", "sip", "phone", "call",
        "remote_control", "remote_access", "virtual_desktop", "screen_sharing"
    },
    
    "out_of_browser_entertainment": {
        "facebook", "instagram", "tiktok", "snapchat", "pinterest",
       "steam", "epic", "gog", "origin", "uplay", "game_launcher",
        "video_player", "audio_player", "music_player", "streaming_client",
       "netflix", "spotify", "disney", "hulu", "twitch", "youtube",
        "ebook", "reader", "kindle", "comic", "book_library",
       "image_viewer", "gallery", "slideshow", "photo_browser",
        "console_emulator", "retro_games", "arcade", "virtual_machine"
    },
    
    "utilities_maintenance": {
        "system_info", "hardware_monitor", "driver_update", "disk_manager",
       "antivirus", "firewall", "encryption", "password_manager", "vpn",
        "file_explorer", "compression", "search_tool", "duplicate_finder",
        "backup", "sync", "cloud_storage", "recovery", "disaster_recovery",
        "cleaner", "optimizer", "performance", "startup_manager", "registry",
      "partition", "format", "recovery", "defrag", "disk_usage",
        "wifi_analyzer", "ip_scanner", "bandwidth_monitor", "packet_analyzer"
    },
    
    "media_creation": {
        "photo_editor", "graphic_design", "raster_editor", "photoshop", "gimp",
        "vector_editor", "illustrator", "inkscape", "svg_editor", "cad",
        "video_editor", "premiere", "final_cut", "davinci", "movie_maker",
        "audio_editor", "daw", "recording", "mixing", "mastering",
        "3d_editor", "blender", "maya", "3ds_max", "sketchup",
        "animation_software", "after_effects", "motion_graphics", "keyframe",
        "layout", "publishing", "indesign", "scribus", "brochure_maker"
    },
    
    "development_programming": {
        "ide", "code_editor", "vscode", "intellij", "eclipse", "sublime",
        "git", "svn", "mercurial", "version_control_client", "github_desktop",
        "database_client", "sql", "nosql", "db_browser", "data_modeling",
        "web_server", "local_web", "xampp", "node", "react", "angular",
        "android_studio", "xcode", "flutter", "react_native", "mobile_emulator",
        "docker", "kubernetes", "ci_cd", "deployment", "container",
        "postman", "insomnia", "api_client", "rest", "graphql"
    },
    
    "others": {
        "specialized", "niche", "industry_specific", "professional",
       "screen_reader", "magnifier", "dictation", "accessibility_aid",
        "vm", "hypervisor", "virtual_machine", "sandbox", "container",
        "fitness", "health_tracker", "meditation", "diet", "sleep",
       "research", "citation", "bibliography", "data_analysis", "statistics",
        "iot", "smart_home", "device_controller", "sensor_monitor",
        "crypto_wallet", "mining", "blockchain", "token", "exchange",
        "education", "learning", "language", "dictionary", "courseware",
        "accounting", "finance", "business", "invoicing", "crm", "analytics"
    }
}
# Energy tag mapping based on main category
ENERGY_TAGS = {
    "internet_browsers": "middle-energy-level",
    "productivity_tools": "low-energy-level",
    "communication_collaboration": "low-energy-level",
    "out_of_browser_entertainment": "high-energy-level",
    "utilities_maintenance": "low-energy-level",
    "media_creation": "high-energy-level",
    "development_programming": "moderate-energy-level",
    "education_learning": "low-energy-level",
    "business_finance": "low-energy-level",
    "others": "moderate-energy-level"
}

# Energy tag colors for UI
ENERGY_COLORS = {
    "high-cpu": "red",
    "moderate-cpu": "orange",
    "low-cpu": "green"
}
