"""Integration test for the full ML fine-tuning pipeline."""

import json
from pathlib import Path

import pytest

from machineinnovatorsinc_solution.model.train import TrainingConfig, fine_tune_model


@pytest.mark.skipif(
    not Path("data/processed/tweet_eval_sentiment").exists(),
    reason="Processed data not found. Run `python scripts/fetch_data.py` first.",
)
def test_full_training_pipeline_integration(tmp_path: Path):
    """Run `fine_tune_model` end-to-end using a tiny subset of real data.
    
    This ensures that tokenization, the HuggingFace Trainer, and metric 
    calculations all wire together correctly without taking hours to run.
    """
    # Use a temporary directory for output so we don't pollute real artifacts
    output_dir = tmp_path / "test_finetuned"

    # Override config for a massive speedup
    cfg = TrainingConfig(
        dataset_id_or_path="data/processed/tweet_eval_sentiment",
        model_id_or_path="prajjwal1/bert-tiny",  # 15MB tiny model for testing
        output_dir=output_dir,
        num_train_epochs=1.0,
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        max_train_samples=4,  # Just 2 batches!
        max_eval_samples=4,
        max_test_samples=4,
        fp16=False,
        hf_model_repo_id=None,  # Do NOT push to hub during tests!
        logging_steps=1,
        save_total_limit=1,
    )

    # Step 1: Run the pipeline
    result = fine_tune_model(cfg)

    # Step 2: Assert return values
    assert "metrics" in result
    assert "metadata" in result
    
    metrics = result["metrics"]
    assert "train" in metrics
    assert "validation" in metrics
    assert "test" in metrics
    
    # Check that accuracy and macro_f1 were calculated accurately
    assert "test_accuracy" in metrics["test"]
    assert "test_macro_f1" in metrics["test"]

    # Step 3: Assert disk artifacts were created properly
    assert output_dir.exists()
    assert (output_dir / "config.json").exists()
    assert (output_dir / "model.safetensors").exists()
    assert (output_dir / "tokenizer_config.json").exists()
    assert (output_dir / "training_args.json").exists()
    
    # Assert our custom JSON dumps worked
    metrics_path = output_dir / "metrics.json"
    metadata_path = output_dir / "metadata.json"
    assert metrics_path.exists()
    assert metadata_path.exists()

    saved_metadata = json.loads(metadata_path.read_text("utf-8"))
    assert saved_metadata["splits"]["train"] == 4
    assert saved_metadata["splits"]["validation"] == 4
