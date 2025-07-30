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

SUBCATEGORIES = {
    "internet_browsers": {
        "web_browsers": ["chrome", "firefox", "safari", "edge", "opera", "brave", "vivaldi", "tor"],
        "browser_extensions": ["adblocker", "password_manager", "vpn", "translator", "screenshot"],
        "download_managers": ["download", "accelerator", "torrent", "file_transfer"],
        "feed_readers": ["rss", "atom", "news_aggregator", "content_reader"],
        "web_development_tools": ["inspector", "web_debugging", "site_analyzer", "lighthouse"]
    },
    
    "productivity_tools": {
        "office_suites": ["microsoft_office", "libreoffice", "openoffice", "wps_office", "google_workspace"],
        "document_editors": ["word_processor", "text_editor", "markdown", "pdf", "note_taking"],
        "spreadsheet_applications": ["excel", "calc", "data_analysis", "formula", "charts"],
        "presentation_software": ["powerpoint", "slides", "presentation_maker", "keynote"],
        "task_management": ["todo", "kanban", "project_management", "time_tracking", "pomodoro"],
        "note_taking_apps": ["evernote", "onenote", "notion", "joplin", "sticky_notes"],
        "calendar_scheduling": ["calendar", "appointment", "reminder", "scheduling", "planner"]
    },
    
    "communication_collaboration": {
        "messaging_apps": ["messenger", "whatsapp", "signal", "telegram", "wechat", "viber"],
        "email_clients": ["mail", "email_manager", "gmail", "outlook", "thunderbird"],
        "video_conferencing": ["zoom", "webex", "skype", "meet", "teams", "video_call"],
        "collaborative_workspaces": ["slack", "discord", "mattermost", "group_editor", "real_time_collab"],
        "social_media_clients": ["social", "network", "twitter", "instagram", "linkedin"],
        "voip_applications": ["voip", "voice_chat", "sip", "phone", "call"],
        "remote_desktop": ["remote_control", "remote_access", "virtual_desktop", "screen_sharing"]
    },
    
    "out_of_browser_entertainment": {
        "social_platforms": ["facebook", "instagram", "tiktok", "snapchat", "pinterest"],
        "game_launchers": ["steam", "epic", "gog", "origin", "uplay", "game_launcher"],
        "media_players": ["video_player", "audio_player", "music_player", "streaming_client"],
        "streaming_services": ["netflix", "spotify", "disney", "hulu", "twitch", "youtube"],
        "ebook_readers": ["ebook", "reader", "kindle", "comic", "book_library"],
        "digital_art_viewers": ["image_viewer", "gallery", "slideshow", "photo_browser"],
        "emulators": ["console_emulator", "retro_games", "arcade", "virtual_machine"]
    },
    
    "utilities_maintenance": {
        "system_utilities": ["system_info", "hardware_monitor", "driver_update", "disk_manager"],
        "security_tools": ["antivirus", "firewall", "encryption", "password_manager", "vpn"],
        "file_management": ["file_explorer", "compression", "search_tool", "duplicate_finder"],
        "backup_recovery": ["backup", "sync", "cloud_storage", "recovery", "disaster_recovery"],
        "system_optimization": ["cleaner", "optimizer", "performance", "startup_manager", "registry"],
        "disk_tools": ["partition", "format", "recovery", "defrag", "disk_usage"],
        "network_tools": ["wifi_analyzer", "ip_scanner", "bandwidth_monitor", "packet_analyzer"]
    },
    
    "media_creation": {
        "image_editing": ["photo_editor", "graphic_design", "raster_editor", "photoshop", "gimp"],
        "vector_graphics": ["vector_editor", "illustrator", "inkscape", "svg_editor", "cad"],
        "video_editing": ["video_editor", "premiere", "final_cut", "davinci", "movie_maker"],
        "audio_production": ["audio_editor", "daw", "recording", "mixing", "mastering"],
        "3d_modeling": ["3d_editor", "blender", "maya", "3ds_max", "sketchup"],
        "animation": ["animation_software", "after_effects", "motion_graphics", "keyframe"],
        "desktop_publishing": ["layout", "publishing", "indesign", "scribus", "brochure_maker"]
    },
    
    "development_programming": {
        "ides_code_editors": ["ide", "code_editor", "vscode", "intellij", "eclipse", "sublime"],
        "version_control": ["git", "svn", "mercurial", "version_control_client", "github_desktop"],
        "database_tools": ["database_client", "sql", "nosql", "db_browser", "data_modeling"],
        "web_development": ["web_server", "local_web", "xampp", "node", "react", "angular"],
        "mobile_development": ["android_studio", "xcode", "flutter", "react_native", "mobile_emulator"],
        "devops_tools": ["docker", "kubernetes", "ci_cd", "deployment", "container"],
        "api_testing": ["postman", "insomnia", "api_client", "rest", "graphql"]
    },
    
    "others": {
        "specialized_tools": ["specialized", "niche", "industry_specific", "professional"],
        "accessibility": ["screen_reader", "magnifier", "dictation", "accessibility_aid"],
        "virtualization": ["vm", "hypervisor", "virtual_machine", "sandbox", "container"],
        "health_wellness": ["fitness", "health_tracker", "meditation", "diet", "sleep"],
        "research_tools": ["research", "citation", "bibliography", "data_analysis", "statistics"],
        "iot_device_management": ["iot", "smart_home", "device_controller", "sensor_monitor"],
        "cryptocurrency": ["crypto_wallet", "mining", "blockchain", "token", "exchange"],
        "education_learning": ["education", "learning", "language", "dictionary", "courseware"],
        "business_finance": ["accounting", "finance", "business", "invoicing", "crm", "analytics"]
    }
}
# Energy tag mapping based on main category
ENERGY_TAGS = {
    "internet_browsers": "moderate-cpu",
    "productivity_tools": "low-cpu",
    "communication_collaboration": "low-cpu",
    "out_of_browser_entertainment": "high-cpu",
    "utilities_maintenance": "low-cpu",
    "media_creation": "high-cpu",
    "development_programming": "moderate-cpu",
    "education_learning": "low-cpu",
    "business_finance": "low-cpu",
    "others": "moderate-cpu"
}

# Energy tag colors for UI
ENERGY_COLORS = {
    "high-cpu": "red",
    "moderate-cpu": "orange",
    "low-cpu": "green"
}
