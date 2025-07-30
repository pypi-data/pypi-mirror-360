# This code is part of Qiskit.
#
# (C) Copyright Alpine Quantum Technologies GmbH 2023
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import importlib.metadata
from typing import Final

QISKIT_VERSION: Final = importlib.metadata.version("qiskit")
QISKIT_AQT_PROVIDER_VERSION: Final = importlib.metadata.version("qiskit-aqt-provider")

__version__: Final = QISKIT_AQT_PROVIDER_VERSION

USER_AGENT_EXTRA: Final = f"qiskit/{QISKIT_VERSION}"
