from src.transform import transform_records


def test_deduplicates_and_limits_records():
    rows = [
        {"id": 1, "name": "repo-a", "full_name": "a/repo-a", "owner": {"login": "a"}},
        {"id": 1, "name": "repo-a", "full_name": "a/repo-a", "owner": {"login": "a"}},
        {"id": 2, "name": "repo-b", "full_name": "b/repo-b", "owner": {"login": "b"}},
    ]
    result = transform_records(rows, target=2)
    assert len(result) == 2
    assert {row["github_id"] for row in result} == {1, 2}
