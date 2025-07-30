import textwrap
from terraback.utils.template_syntax_fixer import TerraformSyntaxFixer


def test_fix_missing_commas_tags(tmp_path):
    tf_content = textwrap.dedent(
        """
        resource "aws_instance" "ex" {
          tags = {"Name" = "example" "Env" = "dev"}
        }
        """
    )
    tf_file = tmp_path / "instance.tf"
    tf_file.write_text(tf_content)

    fixer = TerraformSyntaxFixer(tmp_path)
    fixer.fix_all_files()

    fixed = tf_file.read_text()
    assert 'tags = {"Name" = "example", "Env" = "dev"}' in fixed
    assert 'tags = {,' not in fixed
