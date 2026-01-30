# SATD Collector - Self-Admitted Technical Debt Extraction Tool

This tool automatically extracts and tracks Self-Admitted Technical Debt (SATD) comments from Terraform Infrastructure-as-Code (IaC) repositories.

## Overview

The SATD Collector is a Python-based framework that:
1. **Mines** Terraform repositories for comments
2. **Detects** SATD using keyword-based or ML-based approaches
3. **Tracks** SATD lifecycle across commits (introduction, modification, resolution)
4. **Exports** structured data for analysis

## Architecture

### Core Modules

```
SATD_collector/
├── CommentsMining/          # Comment extraction and SATD detection
│   ├── CommentExtractor.py  # Extract comments from Terraform files
│   ├── SatdDetector.py      # SATD detection strategies
│   └── SatdKeyWordLists.py  # Keyword lists (TODO, FIXME, HACK, etc.)
│
├── Model/                   # Data models
│   ├── Project.py           # Repository representation
│   ├── Commit.py            # Commit metadata
│   ├── File.py              # File tracking
│   ├── Comment.py           # Comment structure
│   ├── SatdComment.py       # SATD comment with metadata
│   ├── SatdCommentList.py   # Collection of SATD comments
│   └── FilesList.py         # Collection of tracked files
│
├── SatdTracking/            # SATD lifecycle tracking
│   ├── AddExecutor.py       # Handle new SATD introduction
│   ├── ModifyExecutor.py    # Handle SATD modifications
│   ├── RenameExecutor.py    # Handle file renames
│   └── DeleteExecutor.py    # Handle SATD removal/resolution
│
├── DataManagment/           # CSV export and data persistence
│   ├── CreateCsvfile.py     # Initialize CSV files
│   ├── AddLineCsv.py        # Append data to CSV
│   └── Utils.py             # Helper functions
│
├── extract_satd_dataset/    # Post-processing
│   └── extract_conc_data.py # Consolidate and extract final dataset
│
├── diagrams/                # Architecture documentation
│   ├── activity_diagrams/   # Workflow diagrams
│   ├── class_diagrams/      # Class structure
│   └── sequence_diagrams/   # Interaction flows
│
└── main.py                  # Entry point
```

## Detection Methods

The tool supports **4 detection strategies**:

| Type | Method | Description |
|------|--------|-------------|
| **1** | KeywordList1 | Basic keywords (TODO, FIXME, HACK, XXX) |
| **2** | KeywordList2 | Extended keyword list |
| **3** | KeywordLists | Combined keyword lists |
| **4** | MLModel | Machine learning-based detection |

## Workflow

### 1. Repository Traversal
- Uses **PyDriller** to traverse Git history
- Processes commits chronologically
- Filters for `.tf` (Terraform) files only

### 2. Comment Extraction
- Extracts all comments from Terraform source code
- Handles single-line (`#`, `//`) and multi-line (`/* */`) comments
- Preserves line numbers and context

### 3. SATD Detection
- Applies selected detection strategy
- Identifies SATD comments based on keywords or ML model
- Creates `SatdComment` objects with metadata

### 4. Lifecycle Tracking
Tracks SATD through file modifications:

| Change Type | Action | Executor |
|-------------|--------|----------|
| **ADD** | New file with SATD | `AddExecutor` |
| **MODIFY** | SATD content changed | `ModifyExecutor` |
| **RENAME** | File renamed | `RenameExecutor` |
| **DELETE** | File/SATD removed | `DeleteExecutor` |

### 5. Data Export
Generates two CSV files:
- **All Comments**: Every comment found (SATD and non-SATD)
- **Tracked SATD**: SATD lifecycle with introduction/resolution info

## Usage

### Basic Usage

```bash
# Run with default settings (KeywordList1)
python main.py --repo_url https://github.com/user/terraform-repo

# Specify detection method
python main.py --repo_url https://github.com/user/terraform-repo --detect_type 3

# Use ML-based detection
python main.py --repo_url https://github.com/user/terraform-repo --detect_type 4
```

### Command-Line Arguments

```bash
--repo_url      # GitHub repository URL (required)
--detect_type   # Detection method: 1, 2, 3, or 4 (default: 1)
```

### Output Files

The tool creates two CSV files in the `dataset/` folder:

1. **`<repo_name>_comments_detect_<type>.csv`**
   - All extracted comments
   - Columns: repo_url, old_path, new_path, comment_text, line_number, total_lines, commit_hash, commit_msg, developer_email, commit_date, is_satd

2. **`<repo_name>_tracked_satd_detect_<type>.csv`**
   - SATD lifecycle tracking
   - Columns: satd_id, repo_url, file_path_first, file_path_last, renamed, keyword, satd_comment, context, bloc_first, bloc_type_first, bloc_last, bloc_type_last, line_first, line_last, commit_hash_first, commit_hash_last, link_first, link_last, introduction_time, last_occurrence, num_commits, addressed

## Architecture Diagrams

The `diagrams/` folder contains visual documentation:

### Activity Diagrams
- **`activity_diagram_framework_detection+classification.png`** - Overall detection workflow
- **`activity_diagram_satd_detector_tracker.png`** - SATD tracking process

### Class Diagrams
- **`models_class_diagram.png`** - Data model structure
- **`satdDetector.png`** - Detector class hierarchy
- **`csvfile_class.png`** - CSV management classes
- **`class_logic.png`** - Core logic classes

### Sequence Diagrams
- **`sequence_diagram.png`** - Main execution flow
- **`sequence_diagram_2.png`** - Detailed interaction patterns

## Key Features

### SATD Lifecycle Tracking
- **Introduction**: First commit where SATD appears
- **Modifications**: Changes to SATD content
- **Resolution**: SATD removal or file deletion
- **File Renames**: Maintains tracking across renames

### Metadata Collection
For each SATD instance:
- Repository URL
- File paths (first and last occurrence)
- Commit hashes (introduction and resolution)
- Developer information
- Timestamps
- Code context (surrounding code blocks)
- Line numbers

### Multi-Repository Support
- Process multiple repositories sequentially
- Consolidated output in `collected_SATD_from_all_projects.csv`
- Project-level statistics in `projects_details.csv`

## Requirements

```bash
pip install -r requirements.txt
```

Key dependencies:
- **PyDriller**: Git repository mining
- **pandas**: Data manipulation
- **scikit-learn**: ML-based detection (if using detect_type=4)

## Output Statistics

After processing, the tool reports:
- Total comments found
- Total SATD comments detected
- SATD percentage
- Number of unique SATD instances
- Addressed vs. unaddressed SATD
- SATD in deleted files

## Integration with RQ1 Taxonomy

The collected SATD data flows into the taxonomy construction:

```
SATD_collector → collected_SATD_from_all_projects.csv → 
RQ1/data_annotation/ → Annotation → Taxonomy
```

See **[Data Annotation README](../data_annotation/README.md)** for the next steps.

## Troubleshooting

### Common Issues

**Issue**: Import errors when running main.py
- **Solution**: Ensure you're running from the `SATD_collector/` directory or set PYTHONPATH

**Issue**: No comments detected
- **Solution**: Verify repository contains `.tf` files and has commit history

**Issue**: ML detector fails
- **Solution**: Ensure ML model files are present and dependencies installed

## Citation

If you use this tool in your research, please cite:

```bibtex
@article{satd_iac_2026,
  title={Self-Admitted Technical Debt in Infrastructure-as-Code},
  author={Your Name},
  year={2026}
}
```

## Related Documentation

- 📖 **[RQ1 Data Annotation](../data_annotation/README.md)** - Annotation workflow
- 📖 **[Root README](../../README.md)** - Project overview
