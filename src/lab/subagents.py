"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Use FIRST, before changing anything, when the task has input files, documentation or a spec you have not "
                "read yet. It reads README files, docstrings, instructions and data samples and reports the facts "
                "(formats, special values, rules). Read-only: it never edits files. Put the task rules and the file paths "
                "in the message."
            ),
            "system_prompt": (
                "You are a read-only explorer. Read the files you are pointed to (README, docstrings, tests, a sample of "
                "the data) and report concrete facts: field formats, special or missing values, duplicates, time zones, "
                "and every rule or convention stated anywhere. Do not create, edit or delete any file. Finish with a "
                "short, factual report that quotes the exact rules you found. Say clearly what you could not verify."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Use to carry out a well-specified change: fix code, write a script that produces an output file, or "
                "generate the required output files. It edits files and runs tests or scripts, then reports what it "
                "changed and the real results. Give it ALL task rules, the exact output file names and their format."
            ),
            "system_prompt": (
                "You are an implementer. Do exactly the change described in the message: fix the root cause rather than "
                "the symptom, follow every stated rule and output format, and keep unrelated files untouched. Run the "
                "tests or a script to check your work and look at the real output. Finish with a short report listing "
                "only the files you really changed or created and what you verified."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Use AFTER the work is done to get an independent check of the result against the task statement: it "
                "re-reads the requirements, inspects the produced files and edge cases, and reports every violation. "
                "Read-only. Give it the full list of requirements and the paths of the files to inspect."
            ),
            "system_prompt": (
                "You are an independent reviewer. Compare the produced files with the requirements in the message, one "
                "requirement at a time. Check output file names, key names, value types, units, ordering and edge "
                "cases, and re-run the tests if there are any. Do not edit files. Report each requirement as OK or "
                "VIOLATED with a one-line reason; do not claim OK for something you did not check."
            ),
        },
    ]
