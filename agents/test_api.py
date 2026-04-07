#!/usr/bin/env python3
"""
Testing script for arch-sense coaching API.
Run test scenarios without needing the frontend.
"""

import asyncio
import json
from typing import Any
import httpx

BASE_URL = "http://localhost:8000"

async def test_api():
    """Run API integration tests."""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        print("🧪 Testing Arch-Sense Coaching API\n")
        
        # 1. Health check
        print("1️⃣  Health Check")
        try:
            resp = await client.get("/health")
            print(f"   Status: {resp.status_code}")
            print(f"   Response: {resp.json()}\n")
        except Exception as e:
            print(f"   ✗ Failed: {e}\n")
            return
        
        # 2. Create session
        print("2️⃣  Create Session")
        try:
            resp = await client.post(
                "/sessions",
                json={
                    "scenario": "Design notification system for 100M users",
                    "user_name": "TestPlayer"
                }
            )
            session = resp.json()
            session_id = session['id']
            print(f"   Status: {resp.status_code}")
            print(f"   Session ID: {session_id}")
            print(f"   Phase: {session['phase']}")
            print(f"   Score: {session['score']}\n")
        except Exception as e:
            print(f"   ✗ Failed: {e}\n")
            return
        
        # 3. Submit initial design
        print("3️⃣  Submit Design (Basic)")
        design = {
            "nodes": [
                {"id": "1", "type": "WEB_SERVER", "label": "Web Server"},
                {"id": "2", "type": "DATABASE", "label": "PostgreSQL"},
            ],
            "edges": [
                {"from": "1", "to": "2"}
            ]
        }
        
        try:
            resp = await client.post(
                f"/sessions/{session_id}/evaluate",
                json={"design": design}
            )
            evaluation = resp.json()
            print(f"   Status: {resp.status_code}")
            print(f"   Feedback items: {len(evaluation['feedback'])}")
            print(f"   Reasoning steps: {len(evaluation['reasoning_steps'])}")
            print(f"   New score: {evaluation['current_score']['total']}")
            
            print("\n   📋 Coach Challenges:")
            for fb in evaluation['feedback']:
                print(f"      • [{fb['coach_type']}] {fb['challenge'][:70]}...")
            
            print("\n   🧠 Reasoning Chain:")
            for i, step in enumerate(evaluation['reasoning_steps'], 1):
                print(f"      {i}. {step[:70]}...")
            print()
        except Exception as e:
            print(f"   ✗ Failed: {e}\n")
            return
        
        # 4. Accept feedback and iterate
        print("4️⃣  Accept Feedback & Iterate")
        design["nodes"].extend([
            {"id": "3", "type": "LOAD_BALANCER", "label": "Load Balancer"},
            {"id": "4", "type": "CACHE", "label": "Redis Cache"},
        ])
        design["edges"].extend([
            {"from": "3", "to": "1"},
            {"from": "1", "to": "4"},
        ])
        
        try:
            # Accept previous feedback
            resp = await client.post(
                f"/sessions/{session_id}/accept-feedback",
                json={"accepted": True, "user_response": "Added LB and cache"}
            )
            print(f"   Feedback accepted: {resp.status_code}")
            
            # Submit improved design
            resp = await client.post(
                f"/sessions/{session_id}/evaluate",
                json={"design": design}
            )
            evaluation = resp.json()
            print(f"   Re-evaluation: {resp.status_code}")
            print(f"   New score: {evaluation['current_score']['total']}")
            print(f"   Score improved: {evaluation['current_score']['total'] > session['score']['total']}")
            print()
        except Exception as e:
            print(f"   ✗ Failed: {e}\n")
        
        # 5. Get progress
        print("5️⃣  Get Progress")
        try:
            resp = await client.get(f"/sessions/{session_id}/progress")
            progress = resp.json()
            print(f"   Status: {resp.status_code}")
            print(f"   Score: {progress['score']['total']}")
            print(f"   Badges: {len(progress['badges'])}")
            print(f"   Difficulty: {progress['difficulty_level']}")
            print(f"   Next Milestone: {progress['next_milestone']}\n")
        except Exception as e:
            print(f"   ✗ Failed: {e}\n")
        
        # 6. Get design evolution
        print("6️⃣  Design Evolution History")
        try:
            resp = await client.get(f"/sessions/{session_id}/design-evolution")
            evolution = resp.json()
            print(f"   Status: {resp.status_code}")
            print(f"   Iterations: {len(evolution['iterations'])}")
            for i, iter_data in enumerate(evolution['iterations'], 1):
                print(f"      Iteration {i}: Score {iter_data['score_before']} → {iter_data['score_after']}")
            print()
        except Exception as e:
            print(f"   ✗ Failed: {e}\n")
        
        # 7. Get session
        print("7️⃣  Get Session Details")
        try:
            resp = await client.get(f"/sessions/{session_id}")
            session = resp.json()
            print(f"   Status: {resp.status_code}")
            print(f"   Phase: {session['phase']}")
            print(f"   Coaching Style: {session['coaching_style']}")
            print(f"   Coach History: {len(session['coach_history'])} interactions")
            print(f"   Badges Earned: {[b['name'] for b in session['badges']]}\n")
        except Exception as e:
            print(f"   ✗ Failed: {e}\n")
        
        # 8. Advance phase
        print("8️⃣  Advance to Stress Phase")
        try:
            resp = await client.post(
                f"/sessions/{session_id}/advance-phase",
                json={"new_phase": "STRESS"}
            )
            print(f"   Status: {resp.status_code}")
            print(f"   Phase advanced to: {resp.json()['phase']}\n")
        except Exception as e:
            print(f"   ✗ Failed: {e}\n")
        
        # 9. List sessions
        print("9️⃣  List All Sessions")
        try:
            resp = await client.get("/sessions")
            sessions = resp.json()
            print(f"   Status: {resp.status_code}")
            print(f"   Total sessions: {len(sessions)}")
            for s in sessions:
                print(f"      • {s['id']}: {s['scenario'][:50]}... (score: {s['score']['total']})")
            print()
        except Exception as e:
            print(f"   ✗ Failed: {e}\n")
        
        # 10. Delete session
        print("🔟 Delete Session")
        try:
            resp = await client.delete(f"/sessions/{session_id}")
            print(f"   Status: {resp.status_code}")
            print(f"   Session deleted\n")
        except Exception as e:
            print(f"   ✗ Failed: {e}\n")
        
        print("="*50)
        print("✅ All tests completed!")
        print("="*50)

if __name__ == "__main__":
    print("⚠️  Make sure the server is running: python main.py\n")
    try:
        asyncio.run(test_api())
    except ConnectionRefusedError:
        print("✗ Could not connect to server at", BASE_URL)
        print("Start the server first: python main.py")
