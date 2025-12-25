#!/usr/bin/env python3
"""
Document Classifier
Uses Claude Code CLI to classify and extract metadata from documents
"""

import json
import subprocess
import tempfile
import os
import sqlite3
from pathlib import Path

class DocumentClassifier:
    """Classify documents using Claude Code CLI"""

    def __init__(self, prompts_dir=None, db_path=None):
        # Auto-detect container vs host environment
        if prompts_dir is None:
            if Path('/app/prompts').exists():
                prompts_dir = '/app/prompts'
            else:
                prompts_dir = '/home/jodfie/scan-processor/prompts'

        if db_path is None:
            if Path('/app/queue/pending.db').exists():
                db_path = '/app/queue/pending.db'
            else:
                db_path = '/home/jodfie/scan-processor/queue/pending.db'

        self.prompts_dir = Path(prompts_dir)
        self.db_path = Path(db_path)

        if not self.prompts_dir.exists():
            raise ValueError(f"Prompts directory does not exist: {self.prompts_dir}")

        self.classifier_prompt = self.prompts_dir / "classifier.md"
        
        # CPS prompts
        self.medical_prompt = self.prompts_dir / "medical.md"
        self.expense_prompt = self.prompts_dir / "expense.md"
        self.schoolwork_prompt = self.prompts_dir / "schoolwork.md"
        
        # Personal prompts
        self.personal_medical_prompt = self.prompts_dir / "personal-medical.md"
        self.personal_expense_prompt = self.prompts_dir / "personal-expense.md"
        self.utility_prompt = self.prompts_dir / "utility.md"
        self.auto_prompt = self.prompts_dir / "auto.md"

    def _call_claude_code(self, file_path, prompt_path, timeout=300, corrections=None):
        """
        Call Claude Code CLI with a file and prompt

        Args:
            file_path: Path to the PDF document
            prompt_path: Path to the prompt file
            timeout: Timeout in seconds (default 5 minutes)
            corrections: Optional dict with user corrections/guidance

        Returns:
            dict: Parsed JSON response from Claude Code
        """
        # Read the prompt
        with open(prompt_path, 'r') as f:
            prompt_text = f.read()

        print(f"Calling Claude Code...")
        print(f"  File: {file_path}")
        print(f"  Prompt: {prompt_path.name}")
        if corrections:
            print(f"  With corrections: {corrections.get('reason', 'yes')}")

        # Create temp file for prompt (auto-cleanup with context manager)
        tmp_fd, tmp_path = tempfile.mkstemp(suffix='.txt', prefix='claude_prompt_')

        try:
            # Write prompt to temp file with file path included
            full_prompt = f"{prompt_text}\n\nPlease analyze this PDF file: {file_path}"

            # Append corrections/guidance if provided
            if corrections and corrections.get('notes'):
                full_prompt += f"\n\n## USER CORRECTIONS / GUIDANCE:\n{corrections['notes']}"
                full_prompt += f"\n\nPlease take these corrections into account when analyzing the document."

            with os.fdopen(tmp_fd, 'w') as tmp_file:
                tmp_file.write(full_prompt)

            # Build command: cat prompt.txt | claude --print --add-dir /path/to/scan-processor
            scan_dir = str(Path(file_path).parent.parent)
            cmd = f'cat {tmp_path} | claude --print --add-dir {scan_dir}'

            # Auto-detect working directory
            if Path('/app').exists():
                work_dir = '/app'
            else:
                work_dir = '/home/jodfie'

            # Execute the command
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=work_dir
            )

            if result.returncode != 0:
                print(f"Claude Code error (exit code {result.returncode}):")
                print(f"STDERR: {result.stderr}")
                raise RuntimeError(f"Claude Code failed: {result.stderr}")

            # Extract JSON from the response
            response_text = result.stdout.strip()

            print(f"✓ Claude Code response received ({len(response_text)} chars)")

            # Try to find JSON in the response
            json_text = self._extract_json(response_text)

            if not json_text:
                print(f"WARNING: Could not extract JSON from response")
                print(f"Response preview: {response_text[:500]}")
                raise ValueError("No JSON found in Claude Code response")

            # Parse the JSON
            data = json.loads(json_text)

            # Log the interaction to database
            self._log_claude_interaction(
                filename=Path(file_path).name,
                prompt_type=self._get_prompt_type(prompt_path),
                prompt_file=prompt_path.name,
                prompt_content=prompt_text,
                response_content=response_text,
                confidence=data.get('confidence'),
                success=True
            )

            # Include prompt and response in return data for history logging
            data['_prompt'] = full_prompt
            data['_response'] = response_text

            return data

        except subprocess.TimeoutExpired:
            print(f"ERROR: Claude Code timed out after {timeout} seconds")
            self._log_claude_interaction(
                filename=Path(file_path).name,
                prompt_type=self._get_prompt_type(prompt_path),
                prompt_file=prompt_path.name,
                prompt_content=full_prompt if 'full_prompt' in locals() else '',
                response_content='',
                success=False,
                error_message=f"Timeout after {timeout} seconds"
            )
            raise
        except Exception as e:
            print(f"ERROR: Failed to call Claude Code: {e}")
            self._log_claude_interaction(
                filename=Path(file_path).name,
                prompt_type=self._get_prompt_type(prompt_path),
                prompt_file=prompt_path.name,
                prompt_content=full_prompt if 'full_prompt' in locals() else '',
                response_content=result.stdout if 'result' in locals() else '',
                success=False,
                error_message=str(e)
            )
            raise
        finally:
            # ALWAYS clean up temp file, even on error
            if os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError as e:
                    print(f"Warning: Could not delete temp file {tmp_path}: {e}")

    def _extract_json(self, text):
        """Extract JSON from markdown code blocks or raw text"""
        import re

        # Try to find JSON in markdown code block
        # Pattern: ```json\n{...}\n```
        json_block_pattern = r'```(?:json)?\s*\n?(\{.*?\})\s*\n?```'
        match = re.search(json_block_pattern, text, re.DOTALL)

        if match:
            return match.group(1)

        # Try to find raw JSON object
        # Pattern: {...}
        json_pattern = r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})'
        match = re.search(json_pattern, text, re.DOTALL)

        if match:
            return match.group(1)

        return None

    def classify_document(self, file_path, corrections=None):
        """
        Classify a document and extract basic metadata

        Args:
            file_path: Path to the PDF document
            corrections: Optional dict with user corrections/guidance

        Returns:
            dict: Classification result with category, metadata, and confidence
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        if not self.classifier_prompt.exists():
            raise FileNotFoundError(f"Classifier prompt not found: {self.classifier_prompt}")

        try:
            # Call Claude Code with the classifier prompt and corrections
            result = self._call_claude_code(file_path, self.classifier_prompt, corrections=corrections)

            print(f"✓ Classification result: {result.get('category', 'UNKNOWN')}")
            print(f"  Confidence: {result.get('confidence', 0):.2%}")

            return result

        except Exception as e:
            print(f"ERROR: Failed to classify document: {e}")
            return {
                'category': 'GENERAL',
                'confidence': 0.0,
                'error': str(e),
                'needs_clarification': True,
                'clarification_question': 'Failed to classify with Claude Code. Please review manually.'
            }

    def extract_medical_metadata(self, file_path, corrections=None):
        """Extract detailed medical metadata"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        if not self.medical_prompt.exists():
            raise FileNotFoundError(f"Medical prompt not found: {self.medical_prompt}")

        try:
            # Call Claude Code with the medical prompt
            result = self._call_claude_code(file_path, self.medical_prompt, corrections=corrections)

            print(f"✓ Medical metadata extracted")
            if result.get('child'):
                print(f"  Child: {result['child']}")
            if result.get('provider'):
                print(f"  Provider: {result['provider']}")

            return result

        except Exception as e:
            print(f"ERROR: Failed to extract medical metadata: {e}")
            return {
                'child': None,
                'date': None,
                'provider': None,
                'type': 'Medical Visit',
                'diagnosis': None,
                'treatment': None,
                'cost': None,
                'needs_clarification': True,
                'clarification_question': f'Failed to extract medical metadata: {str(e)}'
            }

    def extract_expense_metadata(self, file_path, corrections=None):
        """Extract detailed expense metadata"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        if not self.expense_prompt.exists():
            raise FileNotFoundError(f"Expense prompt not found: {self.expense_prompt}")

        try:
            # Call Claude Code with the expense prompt
            result = self._call_claude_code(file_path, self.expense_prompt, corrections=corrections)

            print(f"✓ Expense metadata extracted")
            if result.get('child'):
                print(f"  Child: {result['child']}")
            if result.get('amount'):
                print(f"  Amount: {result['amount']}")

            return result

        except Exception as e:
            print(f"ERROR: Failed to extract expense metadata: {e}")
            return {
                'child': None,
                'date': None,
                'vendor': None,
                'amount': None,
                'category': None,
                'description': None,
                'reimbursable': 'no',
                'needs_clarification': True,
                'clarification_question': f'Failed to extract expense metadata: {str(e)}'
            }

    def extract_schoolwork_metadata(self, file_path, corrections=None):
        """Extract schoolwork metadata"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        if not self.schoolwork_prompt.exists():
            raise FileNotFoundError(f"Schoolwork prompt not found: {self.schoolwork_prompt}")

        try:
            # Call Claude Code with the schoolwork prompt
            result = self._call_claude_code(file_path, self.schoolwork_prompt, corrections=corrections)

            print(f"✓ Schoolwork metadata extracted")
            if result.get('child'):
                print(f"  Child: {result['child']}")
            if result.get('subject'):
                print(f"  Subject: {result['subject']}")

            return result

        except Exception as e:
            print(f"ERROR: Failed to extract schoolwork metadata: {e}")
            return {
                'child': None,
                'subject': None,
                'type': None,
                'grade': None,
                'date': None,
                'tags': ['schoolwork']
            }


    def extract_personal_medical_metadata(self, file_path, corrections=None):
        """Extract personal (adult) medical metadata"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        if not self.personal_medical_prompt.exists():
            raise FileNotFoundError(f"Personal medical prompt not found: {self.personal_medical_prompt}")

        try:
            # Call Claude Code with the personal medical prompt
            result = self._call_claude_code(file_path, self.personal_medical_prompt, corrections=corrections)

            print(f"✓ Personal medical metadata extracted")
            if result.get('provider'):
                print(f"  Provider: {result['provider']}")
            if result.get('type'):
                print(f"  Type: {result['type']}")

            return result

        except Exception as e:
            print(f"ERROR: Failed to extract personal medical metadata: {e}")
            return {
                'date': None,
                'provider': None,
                'type': 'office-visit',
                'specialty': None,
                'diagnosis': None,
                'treatment': None,
                'cost': None,
                'needs_clarification': True,
                'clarification_question': f'Failed to extract personal medical metadata: {str(e)}'
            }

    def extract_personal_expense_metadata(self, file_path, corrections=None):
        """Extract personal expense metadata"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        if not self.personal_expense_prompt.exists():
            raise FileNotFoundError(f"Personal expense prompt not found: {self.personal_expense_prompt}")

        try:
            # Call Claude Code with the personal expense prompt
            result = self._call_claude_code(file_path, self.personal_expense_prompt, corrections=corrections)

            print(f"✓ Personal expense metadata extracted")
            if result.get('vendor'):
                print(f"  Vendor: {result['vendor']}")
            if result.get('amount'):
                print(f"  Amount: ${result['amount']}")

            return result

        except Exception as e:
            print(f"ERROR: Failed to extract personal expense metadata: {e}")
            return {
                'date': None,
                'vendor': None,
                'amount': None,
                'category': 'other',
                'payment_method': None,
                'needs_clarification': True,
                'clarification_question': f'Failed to extract personal expense metadata: {str(e)}'
            }

    def extract_utility_metadata(self, file_path, corrections=None):
        """Extract utility bill metadata"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        if not self.utility_prompt.exists():
            raise FileNotFoundError(f"Utility prompt not found: {self.utility_prompt}")

        try:
            # Call Claude Code with the utility prompt
            result = self._call_claude_code(file_path, self.utility_prompt, corrections=corrections)

            print(f"✓ Utility metadata extracted")
            if result.get('provider'):
                print(f"  Provider: {result['provider']}")
            if result.get('type'):
                print(f"  Type: {result['type']}")
            if result.get('amount'):
                print(f"  Amount: ${result['amount']}")

            return result

        except Exception as e:
            print(f"ERROR: Failed to extract utility metadata: {e}")
            return {
                'date': None,
                'provider': None,
                'type': 'electric',
                'amount': None,
                'due_date': None,
                'account_number': None,
                'needs_clarification': True,
                'clarification_question': f'Failed to extract utility metadata: {str(e)}'
            }

    def extract_auto_metadata(self, file_path, corrections=None):
        """Extract automotive document metadata"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        if not self.auto_prompt.exists():
            raise FileNotFoundError(f"Auto prompt not found: {self.auto_prompt}")

        try:
            # Call Claude Code with the auto prompt
            result = self._call_claude_code(file_path, self.auto_prompt, corrections=corrections)

            print(f"✓ Auto metadata extracted")
            if result.get('provider'):
                print(f"  Provider: {result['provider']}")
            if result.get('type'):
                print(f"  Type: {result['type']}")
            if result.get('amount'):
                print(f"  Amount: ${result['amount']}")

            return result

        except Exception as e:
            print(f"ERROR: Failed to extract auto metadata: {e}")
            return {
                'date': None,
                'type': 'other-service',
                'provider': None,
                'amount': None,
                'vehicle': None,
                'mileage': None,
                'needs_clarification': True,
                'clarification_question': f'Failed to extract auto metadata: {str(e)}'
            }

    def _get_prompt_type(self, prompt_path):
        """Determine prompt type from path"""
        prompt_name = prompt_path.stem.lower()
        
        if 'classifier' in prompt_name:
            return 'classifier'
        # CPS prompts
        elif 'medical' in prompt_name and 'personal' not in prompt_name:
            return 'medical'
        elif 'expense' in prompt_name and 'personal' not in prompt_name:
            return 'expense'
        elif 'schoolwork' in prompt_name:
            return 'schoolwork'
        # Personal prompts
        elif 'personal-medical' in prompt_name:
            return 'personal-medical'
        elif 'personal-expense' in prompt_name:
            return 'personal-expense'
        elif 'utility' in prompt_name:
            return 'utility'
        elif 'auto' in prompt_name:
            return 'auto'
        else:
            return 'unknown'

    def _log_claude_interaction(self, filename, prompt_type, prompt_file,
                                  prompt_content, response_content,
                                  confidence=None, success=True, error_message=None):
        """Log Claude Code interaction to database"""
        try:
            if not self.db_path.exists():
                print(f"Warning: Database not found at {self.db_path}, skipping log")
                return

            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO claude_code_logs
                (filename, prompt_type, prompt_file, prompt_content, response_content,
                 confidence, success, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                filename,
                prompt_type,
                prompt_file,
                prompt_content,
                response_content,
                confidence,
                1 if success else 0,
                error_message
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Warning: Failed to log Claude interaction: {e}")
            # Don't raise - logging failures shouldn't break processing


if __name__ == '__main__':
    import sys

    # Test classifier
    classifier = DocumentClassifier()

    print(f"Classifier initialized")
    print(f"  Prompts directory: {classifier.prompts_dir}")
    print(f"  Classifier prompt: {classifier.classifier_prompt.exists()}")
    print(f"\nCPS Prompts:")
    print(f"  Medical prompt: {classifier.medical_prompt.exists()}")
    print(f"  Expense prompt: {classifier.expense_prompt.exists()}")
    print(f"  Schoolwork prompt: {classifier.schoolwork_prompt.exists()}")
    print(f"\nPersonal Prompts:")
    print(f"  Personal Medical prompt: {classifier.personal_medical_prompt.exists()}")
    print(f"  Personal Expense prompt: {classifier.personal_expense_prompt.exists()}")
    print(f"  Utility prompt: {classifier.utility_prompt.exists()}")
    print(f"  Auto prompt: {classifier.auto_prompt.exists()}")

    # If a file path is provided, test classification
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        print(f"\nTesting classification on: {test_file}")

        result = classifier.classify_document(test_file)
        print(f"\nClassification result:")
        print(json.dumps(result, indent=2))
    else:
        print("\nUsage: python classifier.py <pdf_file>")
        print("Now using Claude Code CLI with your Pro subscription!")
