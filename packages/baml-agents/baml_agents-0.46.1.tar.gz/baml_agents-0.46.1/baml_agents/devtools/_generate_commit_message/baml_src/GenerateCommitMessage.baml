generator target {
    output_type "python/pydantic"
    output_dir ".."
    version "0.201.0"
    default_client_mode sync
}
client<llm> Default {
  provider fallback
  options {
    strategy [
      Claude37Sonnet
      GPT4oDefault
      GPT4oCustom
    ]
  }
}
client<llm> Claude37Sonnet {
  provider anthropic
  options {
    model claude-3-7-sonnet-latest
    api_key env.ANTHROPIC_API_KEY
  }
}
client<llm> GPT4oDefault {
  provider openai
  options {
    model gpt-4o
  }
}
client<llm> GPT4oCustom {
  provider openai
  options {
    model gpt-4o
    api_key env.OPENAI_API_KEY
    base_url env.OPENAI_API_BASE
  }
}

class CommitMessage {
    explanation_feat_vs_no_feat string @description(#"also add explanation short paragraph why you choose feat vs nonfeat for this particular commit."#)
    explanation_comparison string @description(#"also add explanation why its not the three closest category options instead of the one you chose (if you didn't choose build: explain that too)"#)
    explanation_minor_or_patch string @description(#"also add if its MINOR or PATCH change"#)
    conventional_commit_message string @description(#"only oneliners, no multilines"#)
}
function GenerateCommitMessage(git_diff: string, high_level_context: string?) -> CommitMessage {
    client Default
    prompt #"
        help me write conventional commits, just output a good commit message.

        <git_diff>
        {{ git_diff }}
        </git_diff>
        {% if high_level_context %}

        I'll also give you a high level context. You dont need to include all the details i mention, feel free to summarize paraphrase, omit details to make the best commit message, since some of the details I give is just for your context

        <high_level_context>
        {{ high_level_context }}
        </high_level_context>
        {% endif %}

        {{ ctx.output_format }}
    "#
}
test t {
    functions [GenerateCommitMessage]
    args {
        // git diff --staged --ignore-all-space | grep -v "^index" | grep -v "^@@" | sed 's/{{/{/g; s/}}/}/g' | pbcopy
        git_diff #"
            diff --git a/baml_agents/_baml_client_proxy/_hooks/_base_hook.py b/baml_agents/_baml_client_proxy/_hooks/_base_hook.py
            --- a/baml_agents/_baml_client_proxy/_hooks/_base_hook.py
            +++ b/baml_agents/_baml_client_proxy/_hooks/_base_hook.py
                model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)
            
                @classmethod
            -    def from_base_context(cls, base_context: "BaseBamlHookContext") -> Self:
            -        return cls(**base_context.model_dump())
            +    def from_base_context(cls, *, ctx: "BaseBamlHookContext") -> Self:
            +        return cls(**ctx.model_dump())
            
            
            class BaseBamlHook:
        "#
        high_level_context ""
    }
}
