class DryRunDemonstrator:
    """Helper to display dry-run information and collect user feedback."""

    def show_issue(self, title: str, body: str) -> bool:
        print("=== DRY RUN: GitHub issue would be created ===")
        print(f"Title: {title}")
        print(f"Body:\n{body}")
        try:
            answer = input("Proceed after reviewing? [y/N]: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            answer = ""
        
        # Return True only if user explicitly chooses to proceed
        should_proceed = answer in ['y', 'yes']
        
        if should_proceed:
            print("✅ User chose to proceed with issue creation")
        else:
            print("❌ User chose not to proceed, dry-run completed")
            
        return should_proceed

