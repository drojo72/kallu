# KALLU

**Orquestador de asistencia IA seguro y modular**, nacido para potenciar el editor Kate y aliviar el trabajo de desarrolladores.

KALLU no es solo un chat con un LLM. Es un sistema que decide *cuándo* y *si* realmente necesita llamar a un modelo, priorizando privacidad, seguridad de datos y uso eficiente de recursos.

> Estado actual: terminal-first + integración LSP básica con Kate. GUI prevista en fases posteriores.

## Filosofía

- **Seguridad primero**: las claves nunca salen del keyring local. Los LLMs no tienen acceso directo a secretos ni bases de datos.
- **Cascada de decisión**: reglas → búsqueda vectorial → LLM (última opción). El usuario puede forzar el uso de modelos si lo desea.
- **Modular**: cada componente (proveedores LLM, sanitización, vector store, gestión de proyectos, LSP…) es intercambiable.
- **Optimización de recursos**: evitar tokens innecesarios y reutilizar soluciones exitosas.
- **Terminal-first**: validar la lógica core antes de añadir interfaz gráfica.

## Características principales

- Orquestador central que gestiona conexiones a múltiples proveedores (OpenRouter, Google Gemini, y fácilmente extensible a Claude, modelos locales, etc.).
- Integración vía **LSP propio** con Kate.
- Gestión de proyectos GitHub agrupados por *macro-proyectos*, con scopes, reglas y requisitos de recursos por proyecto.
- Pipeline de **sanitización** de todo texto/código saliente (anti-inyección + eliminación de datos sensibles).
- Base de datos **PostgreSQL + pgvector** para almacenar snippets y soluciones exitosas.
- Soporte previsto para modelos locales (detección automática de Ollama, LM Studio, etc. según lo que exista en la máquina del usuario).
- Ejecución en entorno aislado (venv).

## Arquitectura (visión actual)

>Usuario / Kate (LSP)<br>
>↓<br>
>KALLU Core (Python)<br>
>├── Cascada de decisión<br>
>├── Sanitización de salida<br>
>├── Vector Store (pgvector)<br>
>├── Gestión de proyectos & scopes<br>
>└── Proveedores LLM (OpenRouter, Gemini, locales…)<br>

## Estado del proyecto

| Componente              | Estado          |
|-------------------------|-----------------|
| Orquestador core        | En desarrollo   |
| Cascada de decisión     | Diseñado        |
| Sanitización            | Diseñado        |
| Keyring + aislamiento   | Implementado    |
| LSP básico con Kate     | Funcionando (afinando) |
| PostgreSQL + pgvector   | Previsto        |
| GUI                     | Fase posterior  |
| Modelos locales         | Estructura abierta |

## Motivación

KALLU nace de la necesidad de tener asistencia IA **dentro de Kate** de forma segura, controlada y útil, sin enviar más datos de los necesarios y sin depender exclusivamente de un único proveedor.

También se evaluarán proyectos compatibles existentes (como `kate-agents`) para reutilizar buenas ideas de integración con el editor, manteniendo el core de decisión y seguridad propio de KALLU.

## Roadmap inicial

1. Estructura modular del core + abstracción de proveedores
2. Pipeline de sanitización robusto
3. Cascada de decisión (reglas + vector search)
4. Integración estable LSP ↔ Kate
5. Persistencia de snippets exitosos (pgvector)
6. Detección de runtimes locales
7. GUI (fase posterior)

## Contribuciones

El proyecto está en fase muy temprana. Se aceptan ideas, diseños y código, especialmente en:

- Mejoras de seguridad y sanitización
- Abstracciones de proveedores LLM
- Integración LSP
- Esquemas de datos para pgvector orientados a desarrollo

## Licencia

MIT

---

**KALLU** — asistencia IA que piensa antes de gastar tokens.