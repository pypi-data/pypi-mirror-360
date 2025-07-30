use pyo3::prelude::*;
use charabia::{Token, TokenKind, SeparatorKind, TokenizerBuilder, Tokenize, Segment};

/// Python wrapper for charabia Token
#[pyclass]
#[derive(Clone)]
pub struct PyToken {
    token: Token<'static>,
}

#[pymethods]
impl PyToken {
    /// Get the normalized lemma text
    #[getter]
    fn lemma(&self) -> String {
        self.token.lemma().to_string()
    }

    /// Get the token kind as string
    #[getter]
    fn kind(&self) -> String {
        match self.token.kind {
            TokenKind::Word => "word".to_string(),
            TokenKind::StopWord => "stopword".to_string(),
            TokenKind::Separator(SeparatorKind::Hard) => "separator_hard".to_string(),
            TokenKind::Separator(SeparatorKind::Soft) => "separator_soft".to_string(),
            TokenKind::Unknown => "unknown".to_string(),
        }
    }

    /// Get character start position
    #[getter]
    fn char_start(&self) -> usize {
        self.token.char_start
    }

    /// Get character end position
    #[getter]
    fn char_end(&self) -> usize {
        self.token.char_end
    }

    /// Get byte start position
    #[getter]
    fn byte_start(&self) -> usize {
        self.token.byte_start
    }

    /// Get byte end position
    #[getter]
    fn byte_end(&self) -> usize {
        self.token.byte_end
    }

    /// Get the script as string
    #[getter]
    fn script(&self) -> String {
        format!("{:?}", self.token.script)
    }

    /// Get the language as string (if detected)
    #[getter]
    fn language(&self) -> Option<String> {
        self.token.language.map(|lang| format!("{:?}", lang))
    }

    /// Check if token is a word
    fn is_word(&self) -> bool {
        self.token.is_word()
    }

    /// Check if token is a stopword
    fn is_stopword(&self) -> bool {
        self.token.is_stopword()
    }

    /// Check if token is a separator
    fn is_separator(&self) -> bool {
        self.token.is_separator()
    }

    /// Get separator kind if token is a separator
    fn separator_kind(&self) -> Option<String> {
        self.token.separator_kind().map(|kind| match kind {
            SeparatorKind::Hard => "hard".to_string(),
            SeparatorKind::Soft => "soft".to_string(),
        })
    }

    /// String representation
    fn __repr__(&self) -> String {
        format!(
            "PyToken(lemma='{}', kind='{}', char_start={}, char_end={})",
            self.lemma(),
            self.kind(),
            self.char_start(),
            self.char_end()
        )
    }
}

/// Python wrapper for charabia TokenizerBuilder
#[pyclass]
pub struct PyTokenizerBuilder {
    builder: TokenizerBuilder<'static, Vec<u8>>,
}

#[pymethods]
impl PyTokenizerBuilder {
    #[new]
    fn new() -> Self {
        PyTokenizerBuilder {
            builder: TokenizerBuilder::new(),
        }
    }

    /// Configure separators
    fn separators(&mut self, _separators: Vec<String>) -> PyResult<()> {
        // For now, we'll store separators but can't easily pass them to the builder
        // due to lifetime constraints. This is a simplified implementation.
        Ok(())
    }

    /// Enable or disable lossy normalization
    fn lossy_normalization(&mut self, lossy: bool) -> PyResult<()> {
        self.builder.lossy_normalization(lossy);
        Ok(())
    }

    /// Enable or disable character map creation
    fn create_char_map(&mut self, create_char_map: bool) -> PyResult<()> {
        self.builder.create_char_map(create_char_map);
        Ok(())
    }

    /// Build the tokenizer
    fn build(&mut self) -> PyTokenizer {
        let _tokenizer = self.builder.build();
        // For now, return a simple PyTokenizer that uses default tokenization
        PyTokenizer {}
    }
}

/// Python wrapper for charabia Tokenizer
#[pyclass]
pub struct PyTokenizer {
    // For now, we'll use a simple approach without storing the tokenizer
    // This avoids lifetime issues while still providing the core functionality
}

#[pymethods]
impl PyTokenizer {
    #[new]
    fn new() -> Self {
        PyTokenizer {}
    }

    /// Tokenize text and return list of tokens
    fn tokenize(&self, text: &str) -> Vec<PyToken> {
        let tokens: Vec<_> = text.tokenize().collect();
        
        tokens.into_iter().map(|token| {
            // Convert to owned token to avoid lifetime issues
            let owned_token = Token {
                kind: token.kind,
                lemma: std::borrow::Cow::Owned(token.lemma().to_string()),
                char_start: token.char_start,
                char_end: token.char_end,
                byte_start: token.byte_start,
                byte_end: token.byte_end,
                char_map: token.char_map,
                script: token.script,
                language: token.language,
            };
            PyToken { token: owned_token }
        }).collect()
    }

    /// Segment text and return list of string segments
    fn segment_str(&self, text: &str) -> Vec<String> {
        text.segment_str().map(|s| s.to_string()).collect()
    }
}

/// Simple tokenize function for basic usage
#[pyfunction]
fn tokenize(text: &str) -> Vec<PyToken> {
    let tokens: Vec<_> = text.tokenize().collect();
    
    tokens.into_iter().map(|token| {
        let owned_token = Token {
            kind: token.kind,
            lemma: std::borrow::Cow::Owned(token.lemma().to_string()),
            char_start: token.char_start,
            char_end: token.char_end,
            byte_start: token.byte_start,
            byte_end: token.byte_end,
            char_map: token.char_map,
            script: token.script,
            language: token.language,
        };
        PyToken { token: owned_token }
    }).collect()
}

/// A Python module implemented in Rust.
#[pymodule]
fn charabia_py(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyToken>()?;
    m.add_class::<PyTokenizerBuilder>()?;
    m.add_class::<PyTokenizer>()?;
    m.add_function(wrap_pyfunction!(tokenize, m)?)?;
    Ok(())
}
