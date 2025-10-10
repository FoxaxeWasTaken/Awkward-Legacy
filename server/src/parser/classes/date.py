class Date:
    """Date and calendar modifiers"""
    def __init__(self, date_str: str = None):
        self.date_str = None
        self.modifier = None  # ~, ?, <, >, |, ..
        self.calendar = 'G'  # G: Grégorien, J: Julien, F: Français, H: Hébreu
        self.text_date = None
        
        if date_str:
            self._parse_date(date_str)
    
    def _parse_date(self, date_str: str):
        # textual date(0(...))
        if date_str.startswith('0(') and date_str.endswith(')'):
            self.text_date = date_str[2:-1]
            return
            
        # Modifiers
        modifiers = {'~': 'about', '?': 'maybe', '<': 'before', '>': 'after'}
        for mod_char, mod_name in modifiers.items():
            if date_str.startswith(mod_char):
                self.modifier = mod_name
                date_str = date_str[1:]
                break
        
        # calendar
        if date_str and date_str.endswith(('J', 'F', 'H')):
            self.calendar = date_str[-1]
            date_str = date_str[:-1]
        
        self.date_str = date_str
    
    def __str__(self):
        if self.text_date:
            return self.text_date
        return self.date_str or ""