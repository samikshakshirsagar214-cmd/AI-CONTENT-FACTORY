## Architecture Overview

The system follows a modular, agent-based architecture.

- Manager Agent controls execution and scheduling
- Individual agents perform isolated tasks
- APIs are used only where necessary to minimize cost
- Local execution for testing
- Cloud deployment for production

This architecture allows:
- Easy scaling
- Fault isolation
- Incremental feature addition