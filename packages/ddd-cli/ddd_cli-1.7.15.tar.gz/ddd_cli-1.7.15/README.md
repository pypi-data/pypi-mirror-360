# DDD CLI

This package adds custom commands to Django to make it easier to implement a Domain-Driven Design (DDD) architecture.

## Available commands

- `ddd create-entity <app_path> <entity_name> [--split]`
- `ddd create-service <app_path> <entity_name> [--class-format] [--split]`
- `ddd create-repository <app_path> <entity_name>`
- `ddd create-dto <app_path> <dto_name> [--split]`
- `ddd create-serializer <app_path> <serializer_name> [--split]`
- `ddd create-view-api-apiview <app_path> <entity_name>`
- `ddd create-view-api-viewset <app_path> <entity_name>`
- `ddd create-view <app_path> <entity_name>`

## Show help
- `ddd --help`