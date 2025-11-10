"""Quick test script for design workflow."""
import asyncio
import httpx
import json


async def test_simple_design():
    """Test a simple design creation."""
    base_url = "http://localhost:8000"

    async with httpx.AsyncClient(base_url=base_url, timeout=60.0) as client:
        print("Starting design session...")

        # Start session
        response = await client.post("/api/v1/design/start", json={
            "prompt": "Create a simple mounting bracket, 50mm x 30mm x 20mm, with 4 corner holes"
        })

        if response.status_code != 200:
            print(f"Error: {response.text}")
            return

        data = response.json()
        session_id = data["session_id"]
        print(f"Session ID: {session_id}")

        # Process request
        print("\nProcessing design request...")
        response = await client.post("/api/v1/design/process", json={
            "session_id": session_id,
            "message": "Create a simple mounting bracket, 50mm x 30mm x 20mm, with 4 corner holes of 5mm diameter. Material: PLA. Manufacturing: FDM 3D printing."
        })

        result = response.json()
        print(f"Status: {result['status']}")

        # Handle clarifications
        max_iterations = 10
        iteration = 0

        while result["status"] == "awaiting_clarification" and iteration < max_iterations:
            print(f"\nQuestions from agent:")
            for q in result.get("questions", []):
                print(f"  - {q}")

            # Get user input
            answer = input("\nYour answer: ")

            response = await client.post("/api/v1/design/process", json={
                "session_id": session_id,
                "message": answer
            })

            result = response.json()
            print(f"Status: {result['status']}")
            iteration += 1

        # Check final status
        if result["status"] == "complete":
            print("\n✓ Design complete!")
            print(f"Design ID: {result.get('design_id')}")
            print(f"File ID: {result.get('file_id')}")
            print(f"Download URL: {result.get('download_url')}")

            # Download STL
            print("\nDownloading STL file...")
            response = await client.get(f"/api/v1/design/{session_id}/download")

            if response.status_code == 200:
                filename = f"design_{session_id}.stl"
                with open(filename, "wb") as f:
                    f.write(response.content)
                print(f"✓ STL file saved: {filename}")
            else:
                print(f"Error downloading: {response.text}")

        else:
            print(f"\n✗ Design failed with status: {result['status']}")


if __name__ == "__main__":
    print("="*60)
    print("THEO CAD - Design Workflow Test")
    print("="*60)
    print()

    asyncio.run(test_simple_design())
