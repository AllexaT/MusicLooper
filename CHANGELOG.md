# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [4.1] - 2025-01-25

### Added
- YouTube Music Download & Analysis Support

### Fixed
- Remove unnecessary requirements from requirements.txt.

## [4.0] - 2025-01-25

### Added
- GUI interface with support for drag-and-drop music files
- Automatic detection of music loop points
- Real-time preview feature to listen to loop effects
- Support for common audio formats such as WAV, MP3, FLAC, OGG
- Volume control and playback progress display
- Sorting loop points by score or length
- Bilingual support for Chinese and English
- Automatic detection of system FFmpeg, with download option if not available
- Support for local FFmpeg folder

### Features
- Modern interface developed with PyQt6
- Analyzes music structure to find the best loop points
- Real-time audio processing and seamless loop playback
- Automatic detection of system language to switch interface language
- User-friendly error prompts and guidance
