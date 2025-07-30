import asyncio
from gitupdater import GitUpdater

async def main():
    # Define repository, current version, and tool name
    repo = "RevoltSecurities/Subprober"
    current_version = "v1.0.3"
    toolname = "subprober"

    # Create and use the updater inside async context manager
    async with GitUpdater(repo, current_version, toolname) as updater:
        # Show version comparison
        await updater.versionlog()

        # Optional: Show changelog/notes
        await updater.show_update_log()

        # Perform update
        updated = await updater.update()
        if updated:
            print(f"[+] {toolname} update complete.")
        else:
            print(f"[-] {toolname} update failed or already up to date.")

# Run the async function
if __name__ == "__main__":
    asyncio.run(main())
