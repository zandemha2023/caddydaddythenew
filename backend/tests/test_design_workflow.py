"""Test cases for the complete design workflow."""
import pytest
import asyncio
from httpx import AsyncClient
import json
import websockets
from pathlib import Path

# Test base URL (change for production)
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"


class TestDesignWorkflow:
    """Test complete design workflow from prompt to STL."""

    @pytest.mark.asyncio
    async def test_simple_cube(self):
        """Test simple design: 50mm cube."""
        async with AsyncClient(base_url=BASE_URL) as client:
            # Start session
            response = await client.post("/api/v1/design/start", json={
                "prompt": "Create a 50mm cube"
            })
            assert response.status_code == 200
            data = response.json()
            session_id = data["session_id"]

            print(f"\n[TEST] Started session: {session_id}")

            # Process request
            response = await client.post("/api/v1/design/process", json={
                "session_id": session_id,
                "message": "Create a 50mm cube"
            })
            assert response.status_code == 200
            result = response.json()

            print(f"[TEST] Status: {result['status']}")

            # Handle clarifications if needed
            max_iterations = 5
            iteration = 0

            while result["status"] == "awaiting_clarification" and iteration < max_iterations:
                print(f"[TEST] Questions: {result.get('questions', [])}")

                # Auto-respond to clarifications
                if "dimension" in str(result.get('questions', [])).lower():
                    answer = "50mm on all sides"
                elif "material" in str(result.get('questions', [])).lower():
                    answer = "PLA"
                elif "tolerance" in str(result.get('questions', [])).lower():
                    answer = "Standard ±0.2mm"
                else:
                    answer = "Yes, that's correct"

                print(f"[TEST] Answering: {answer}")

                response = await client.post("/api/v1/design/process", json={
                    "session_id": session_id,
                    "message": answer
                })
                result = response.json()
                iteration += 1

            # Should be complete now
            assert result["status"] == "complete", f"Expected complete, got {result['status']}"
            assert "file_path" in result or "download_url" in result

            print(f"[TEST] Design complete! File: {result.get('file_path', 'N/A')}")

            # Download STL
            response = await client.get(f"/api/v1/design/{session_id}/download")
            assert response.status_code == 200
            assert response.headers["content-type"] == "model/stl"

            print("[TEST] ✓ Simple cube test passed!")

    @pytest.mark.asyncio
    async def test_phone_stand(self):
        """Test medium complexity: phone stand."""
        async with AsyncClient(base_url=BASE_URL) as client:
            # Start session
            response = await client.post("/api/v1/design/start", json={
                "prompt": "Create a phone stand that holds phone at 60 degrees"
            })
            session_id = response.json()["session_id"]

            print(f"\n[TEST] Phone stand session: {session_id}")

            # Process request
            response = await client.post("/api/v1/design/process", json={
                "session_id": session_id,
                "message": "Create a phone stand that holds phone at 60 degrees"
            })
            result = response.json()

            # Handle clarifications
            max_iterations = 10
            iteration = 0

            while result["status"] == "awaiting_clarification" and iteration < max_iterations:
                print(f"[TEST] Questions: {result.get('questions', [])}")

                # Smart responses
                questions_lower = str(result.get('questions', [])).lower()

                if "phone size" in questions_lower or "width" in questions_lower:
                    answer = "For a standard phone, 80mm wide, 10mm thick"
                elif "height" in questions_lower or "tall" in questions_lower:
                    answer = "100mm tall total"
                elif "base" in questions_lower:
                    answer = "Make the base 120mm x 80mm for stability"
                elif "material" in questions_lower:
                    answer = "PLA plastic"
                elif "weight" in questions_lower or "load" in questions_lower:
                    answer = "Needs to support 200g phone weight"
                else:
                    answer = "Yes, proceed with those specifications"

                print(f"[TEST] Answering: {answer}")

                response = await client.post("/api/v1/design/process", json={
                    "session_id": session_id,
                    "message": answer
                })
                result = response.json()
                iteration += 1

            assert result["status"] == "complete"
            print(f"[TEST] ✓ Phone stand test passed!")

    @pytest.mark.asyncio
    async def test_gear(self):
        """Test complex design: gear with teeth."""
        async with AsyncClient(base_url=BASE_URL) as client:
            response = await client.post("/api/v1/design/start", json={
                "prompt": "Create a gear with 20 teeth, 50mm diameter"
            })
            session_id = response.json()["session_id"]

            print(f"\n[TEST] Gear session: {session_id}")

            response = await client.post("/api/v1/design/process", json={
                "session_id": session_id,
                "message": "Create a gear with 20 teeth, 50mm diameter"
            })
            result = response.json()

            # Handle clarifications
            max_iterations = 10
            iteration = 0

            while result["status"] == "awaiting_clarification" and iteration < max_iterations:
                print(f"[TEST] Questions: {result.get('questions', [])}")

                questions_lower = str(result.get('questions', [])).lower()

                if "thickness" in questions_lower or "height" in questions_lower:
                    answer = "10mm thick"
                elif "bore" in questions_lower or "center hole" in questions_lower or "shaft" in questions_lower:
                    answer = "6mm center bore for shaft"
                elif "module" in questions_lower or "tooth" in questions_lower:
                    answer = "Module 2.5"
                elif "material" in questions_lower:
                    answer = "PLA"
                elif "pressure angle" in questions_lower:
                    answer = "20 degrees pressure angle"
                else:
                    answer = "Yes, that's correct"

                print(f"[TEST] Answering: {answer}")

                response = await client.post("/api/v1/design/process", json={
                    "session_id": session_id,
                    "message": answer
                })
                result = response.json()
                iteration += 1

            assert result["status"] == "complete"
            print(f"[TEST] ✓ Gear test passed!")

    @pytest.mark.asyncio
    async def test_websocket_streaming(self):
        """Test WebSocket real-time updates."""
        async with AsyncClient(base_url=BASE_URL) as client:
            # Start session
            response = await client.post("/api/v1/design/start", json={
                "prompt": "Create a 30mm cube"
            })
            session_id = response.json()["session_id"]

            print(f"\n[TEST] WebSocket session: {session_id}")

            messages_received = []

            # Connect to WebSocket
            async with websockets.connect(f"{WS_URL}/api/v1/design/ws/{session_id}") as ws:
                # Start processing in background
                async def process_request():
                    await asyncio.sleep(0.5)  # Let WS connect
                    async with AsyncClient(base_url=BASE_URL) as client2:
                        await client2.post("/api/v1/design/process", json={
                            "session_id": session_id,
                            "message": "Create a 30mm cube, PLA material"
                        })

                # Start processing
                asyncio.create_task(process_request())

                # Receive messages with timeout
                try:
                    async with asyncio.timeout(30):
                        async for message in ws:
                            data = json.loads(message)
                            messages_received.append(data)
                            print(f"[TEST] WS: {data.get('type')} - {data.get('stage', data.get('message', ''))}")

                            if data.get("type") == "complete":
                                break
                except asyncio.TimeoutError:
                    print("[TEST] WebSocket timeout")

            # Verify we received messages
            assert len(messages_received) > 0
            message_types = [msg.get("type") for msg in messages_received]

            # Should have at least: connected, progress, complete (or similar)
            assert "connected" in message_types or "progress" in message_types

            print(f"[TEST] ✓ Received {len(messages_received)} WebSocket messages")


async def run_all_tests():
    """Run all tests sequentially."""
    print("\n" + "="*60)
    print("THEO CAD - Design Workflow Tests")
    print("="*60)

    test = TestDesignWorkflow()

    try:
        print("\n>>> Test 1: Simple Cube")
        await test.test_simple_cube()

        print("\n>>> Test 2: Phone Stand")
        await test.test_phone_stand()

        print("\n>>> Test 3: Gear")
        await test.test_gear()

        print("\n>>> Test 4: WebSocket Streaming")
        await test.test_websocket_streaming()

        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run tests
    asyncio.run(run_all_tests())
