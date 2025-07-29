use std::borrow::Cow;

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct DocumentLink {
    pub target: tower_lsp::lsp_types::Url,
    pub range: tombi_text::Range,
    pub tooltip: Cow<'static, str>,
}

impl From<DocumentLink> for tower_lsp::lsp_types::DocumentLink {
    fn from(value: DocumentLink) -> Self {
        tower_lsp::lsp_types::DocumentLink {
            range: value.range.into(),
            target: Some(value.target),
            tooltip: Some(value.tooltip.into_owned()),
            data: None,
        }
    }
}
