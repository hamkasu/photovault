print("Testing imports...") 
try: 
    from photovault import create_app 
    print("Import successful!") 
    app = create_app() 
    print("App creation successful!") 
except Exception as e: 
    print(f"Error: {e}") 
