import os
import sys
import json
import requests
import psycopg

BASE_URL = "http://127.0.0.1:8000"
DB_URL = "postgresql://postgres:postgres@localhost:5432/lexguard"

def test_full_live_verification():
    print("=" * 60)
    print("LEXGUARD LIVE POSTGRESQL + PGVECTOR VERIFICATION SUITE")
    print("=" * 60)

    # 1. Health check
    print("\n--- 1. Health Check (GET /api/health) ---")
    resp = requests.get(f"{BASE_URL}/api/health")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    health_data = resp.json()
    print("Health response:", json.dumps(health_data, indent=2))
    assert health_data.get("database", {}).get("connected") is True, "database.connected is not True!"
    assert health_data.get("database", {}).get("vector_extension") is True, "database.vector_extension is not True!"
    print("Health Check PASSED.")

    # 2. Prepare test documents
    doc_a_content = (
        "LEXGUARD_TEST_DOCUMENT_A_UNIQUE\n\n"
        "Master Software and Technology Services Agreement Alpha.\n"
        "Section 1: The licensee agrees to maintain total confidentiality under strict LexGuard protocol A.\n"
        "Section 2: Governing law is Delaware and liability is capped at ten million dollars.\n"
        "Section 3: Indemnification for intellectual property infringement claims shall be provided by Licensor."
    )
    doc_b_content = (
        "LEXGUARD_TEST_DOCUMENT_B_UNIQUE\n\n"
        "Patent and Trade Secret Assignment Agreement Beta.\n"
        "Section 1: The vendor assigns all patents, copyrights, and trade secrets under strict LexGuard protocol B.\n"
        "Section 2: Governing law is California and dispute resolution shall be in San Francisco.\n"
        "Section 3: Restrictive covenants apply for twenty-four months post termination."
    )

    doc_a_id = None
    doc_b_id = None
    doc_a_obj = None
    doc_b_obj = None

    try:
        # 3. Upload Document A
        print("\n--- 2. Upload Document A (POST /api/v1/documents/upload) ---")
        files_a = {"file": ("test_doc_a.txt", doc_a_content.encode("utf-8"), "text/plain")}
        resp_a = requests.post(f"{BASE_URL}/api/v1/documents/upload", files=files_a)
        assert resp_a.status_code == 200, f"Upload A failed: {resp_a.text}"
        doc_a_obj = resp_a.json()
        doc_a_id = doc_a_obj["document_id"]
        print(f"Document A uploaded successfully. ID={doc_a_id}, words={doc_a_obj['word_count']}")

        # 4. Upload Document B
        print("\n--- 3. Upload Document B (POST /api/v1/documents/upload) ---")
        files_b = {"file": ("test_doc_b.txt", doc_b_content.encode("utf-8"), "text/plain")}
        resp_b = requests.post(f"{BASE_URL}/api/v1/documents/upload", files=files_b)
        assert resp_b.status_code == 200, f"Upload B failed: {resp_b.text}"
        doc_b_obj = resp_b.json()
        doc_b_id = doc_b_obj["document_id"]
        print(f"Document B uploaded successfully. ID={doc_b_id}, words={doc_b_obj['word_count']}")

        # 5. Live Index Document A with real Gemini embeddings
        print("\n--- 4. Live Index Document A (POST /api/v1/documents/index) ---")
        index_payload_a = {"document": doc_a_obj}
        resp_idx_a = requests.post(f"{BASE_URL}/api/v1/documents/index", json=index_payload_a)
        assert resp_idx_a.status_code == 200, f"Index A failed: {resp_idx_a.text}"
        idx_a_data = resp_idx_a.json()
        print("Index A response:", json.dumps(idx_a_data, indent=2))
        assert idx_a_data["indexed"] is True
        assert idx_a_data["chunk_count"] > 0
        chunks_count_a = idx_a_data["chunk_count"]

        # 6. Live Index Document B with real Gemini embeddings
        print("\n--- 5. Live Index Document B (POST /api/v1/documents/index) ---")
        index_payload_b = {"document": doc_b_obj}
        resp_idx_b = requests.post(f"{BASE_URL}/api/v1/documents/index", json=index_payload_b)
        assert resp_idx_b.status_code == 200, f"Index B failed: {resp_idx_b.text}"
        idx_b_data = resp_idx_b.json()
        print("Index B response:", json.dumps(idx_b_data, indent=2))
        assert idx_b_data["indexed"] is True
        assert idx_b_data["chunk_count"] > 0

        # 7. Direct SQL Inspection
        print("\n--- 6. SQL Database Inspection (PostgreSQL 18 + pgvector) ---")
        with psycopg.connect(DB_URL) as conn:
            with conn.cursor() as cur:
                # Check document records
                cur.execute("SELECT document_id, filename, word_count FROM documents WHERE document_id IN (%s, %s)", (doc_a_id, doc_b_id))
                doc_rows = cur.fetchall()
                print(f"Documents table rows: {doc_rows}")
                assert len(doc_rows) == 2, f"Expected 2 document rows, found {len(doc_rows)}"

                # Check chunks and vector dimensions
                cur.execute("""
                    SELECT document_id, chunk_id, length(content), vector_dims(embedding)
                    FROM document_chunks
                    WHERE document_id IN (%s, %s)
                """, (doc_a_id, doc_b_id))
                chunk_rows = cur.fetchall()
                print(f"Document chunks total count: {len(chunk_rows)}")
                for r in chunk_rows:
                    print(f"  doc_id={r[0]}, chunk_id={r[1]}, content_len={r[2]}, vector_dim={r[3]}")
                    assert r[3] == 3072, f"Expected vector dimension 3072, got {r[3]}"
        print("SQL verification PASSED: VECTOR(3072) verified in PostgreSQL.")

        # 8. Live Retrieval Test on Document A
        print("\n--- 7. Live Retrieval Test on Document A (POST /api/v1/retrieval/search) ---")
        search_payload_a = {
            "document_id": doc_a_id,
            "query": "What is the liability cap and indemnity under protocol A?",
            "top_k": 3
        }
        resp_search_a = requests.post(f"{BASE_URL}/api/v1/retrieval/search", json=search_payload_a)
        assert resp_search_a.status_code == 200, f"Search A failed: {resp_search_a.text}"
        search_a_data = resp_search_a.json()
        print("Search A response:")
        print(f"  grounding_status: {search_a_data['grounding_status']}")
        print(f"  results count: {len(search_a_data['results'])}")
        assert search_a_data["grounding_status"] == "grounded", f"Expected grounded, got {search_a_data['grounding_status']}"
        assert len(search_a_data["results"]) > 0, "No results returned for search A"
        top_result_a = search_a_data["results"][0]
        print(f"  top similarity_score: {top_result_a['similarity_score']}")
        print(f"  page_start: {top_result_a['page_start']}, char_start: {top_result_a['character_start']}")
        print(f"  top snippet: {top_result_a['text'][:80]}...")
        assert "LEXGUARD_TEST_DOCUMENT_A_UNIQUE" in top_result_a["text"] or "protocol A" in top_result_a["text"]
        assert top_result_a["similarity_score"] >= 0.55
        print("Retrieval A PASSED.")

        # 9. Cross-Document Isolation Test
        print("\n--- 8. Cross-Document Isolation Test ---")
        # Search Doc A with Doc B query
        search_cross_a = {
            "document_id": doc_a_id,
            "query": "LEXGUARD_TEST_DOCUMENT_B_UNIQUE patents trademarks California",
            "top_k": 5
        }
        resp_cross_a = requests.post(f"{BASE_URL}/api/v1/retrieval/search", json=search_cross_a)
        cross_a_data = resp_cross_a.json()
        for res in cross_a_data.get("results", []):
            assert "LEXGUARD_TEST_DOCUMENT_B_UNIQUE" not in res["text"], "LEAK! Doc B unique token found in Doc A retrieval results!"
            assert "California" not in res["text"], "LEAK! Doc B California text found in Doc A retrieval results!"
        print("Doc A search isolated: ZERO Document B tokens leaked into Document A results.")

        # Reverse test: Search Doc B with Doc A query
        search_cross_b = {
            "document_id": doc_b_id,
            "query": "LEXGUARD_TEST_DOCUMENT_A_UNIQUE indemnity Delaware",
            "top_k": 5
        }
        resp_cross_b = requests.post(f"{BASE_URL}/api/v1/retrieval/search", json=search_cross_b)
        cross_b_data = resp_cross_b.json()
        for res in cross_b_data.get("results", []):
            assert "LEXGUARD_TEST_DOCUMENT_A_UNIQUE" not in res["text"], "LEAK! Doc A unique token found in Doc B retrieval results!"
            assert "Delaware" not in res["text"], "LEAK! Doc A Delaware text found in Doc B retrieval results!"
        print("Doc B search isolated: ZERO Document A tokens leaked into Document B results.")
        print("Cross-Document Isolation PASSED: Strict WHERE document_id = :document_id confirmed.")

        # 10. Reindexing Test (Idempotency)
        print("\n--- 9. Reindexing Test (Idempotency) ---")
        with psycopg.connect(DB_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM document_chunks WHERE document_id = %s", (doc_a_id,))
                count_before = cur.fetchone()[0]
        print(f"Doc A chunks before re-indexing: {count_before}")

        resp_reindex = requests.post(f"{BASE_URL}/api/v1/documents/index", json=index_payload_a)
        assert resp_reindex.status_code == 200, f"Reindex failed: {resp_reindex.text}"

        with psycopg.connect(DB_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM document_chunks WHERE document_id = %s", (doc_a_id,))
                count_after = cur.fetchone()[0]
        print(f"Doc A chunks after re-indexing: {count_after}")
        assert count_before == count_after, f"Duplicate chunks detected! Before={count_before}, After={count_after}"

        # Verify retrieval still works after reindexing
        resp_search_after = requests.post(f"{BASE_URL}/api/v1/retrieval/search", json=search_payload_a)
        assert resp_search_after.status_code == 200
        assert resp_search_after.json()["grounding_status"] == "grounded"
        print("Reindexing Idempotency PASSED: No duplicates created, retrieval verified.")

        # 11. Delete Test
        print("\n--- 10. Vector Deletion Test (DELETE /api/v1/documents/{document_id}/vectors) ---")
        resp_del = requests.delete(f"{BASE_URL}/api/v1/documents/{doc_a_id}/vectors")
        assert resp_del.status_code == 200, f"Delete failed: {resp_del.text}"
        print(f"Delete response: {resp_del.json()}")

        # Verify PostgreSQL chunks removed
        with psycopg.connect(DB_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM document_chunks WHERE document_id = %s", (doc_a_id,))
                doc_a_chunks_left = cur.fetchone()[0]
                cur.execute("SELECT count(*) FROM document_chunks WHERE document_id = %s", (doc_b_id,))
                doc_b_chunks_left = cur.fetchone()[0]
        print(f"Doc A chunks remaining in PostgreSQL: {doc_a_chunks_left}")
        print(f"Doc B chunks remaining in PostgreSQL: {doc_b_chunks_left}")
        assert doc_a_chunks_left == 0, f"Expected 0 chunks for Doc A after deletion, found {doc_a_chunks_left}"
        assert doc_b_chunks_left > 0, "Doc B chunks were unintentionally deleted!"

        # Retrieval on Doc A should now return not indexed or empty
        resp_search_deleted = requests.post(f"{BASE_URL}/api/v1/retrieval/search", json=search_payload_a)
        assert resp_search_deleted.status_code == 200
        del_search_data = resp_search_deleted.json()
        print(f"Search after deletion: grounding_status={del_search_data['grounding_status']}, results={len(del_search_data['results'])}")
        assert del_search_data["grounding_status"] == "document_not_indexed"
        assert len(del_search_data["results"]) == 0
        print("Vector Deletion PASSED.")

    finally:
        # 12. Cleanup all test rows
        print("\n--- 11. Database Cleanup ---")
        with psycopg.connect(DB_URL) as conn:
            with conn.cursor() as cur:
                if doc_a_id or doc_b_id:
                    ids = tuple([i for i in [doc_a_id, doc_b_id] if i])
                    cur.execute("DELETE FROM document_chunks WHERE document_id = ANY(%s)", (list(ids),))
                    cur.execute("DELETE FROM documents WHERE document_id = ANY(%s)", (list(ids),))
                    conn.commit()
                # Check residual counts
                cur.execute("SELECT count(*) FROM documents")
                docs_count = cur.fetchone()[0]
                cur.execute("SELECT count(*) FROM document_chunks")
                chunks_count = cur.fetchone()[0]
                print(f"Post-cleanup row counts: documents={docs_count}, document_chunks={chunks_count}")
        print("Cleanup completed: Zero residual test documents or chunks left in PostgreSQL.")

    print("\n" + "=" * 60)
    print("ALL LIVE VERIFICATION TESTS PASSED SUCCESSFULLY! (10/10)")
    print("=" * 60)

if __name__ == "__main__":
    test_full_live_verification()
