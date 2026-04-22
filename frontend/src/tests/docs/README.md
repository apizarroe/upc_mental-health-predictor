# Guía de Testing — Mental Health Predictor

Utilidades, fixtures y mocks para escribir tests en el proyecto.

## Estructura

```
tests/
├── fixtures/          # Datos de prueba reutilizables
│   ├── pacientes.js
│   ├── especialistas.js
│   ├── historias.js
│   └── index.js
├── mocks/             # Funciones y servicios simulados
│   ├── api.js
│   ├── navigation.js
│   └── index.js
└── utils/             # Utilidades para tests
    ├── test-helpers.js
    ├── validators.js
    └── index.js
```

## Fixtures

Datos de prueba predefinidos para usar en tests.

```javascript
import { pacienteValido, listaPacientes } from '../tests/fixtures';

it('debe crear un paciente válido', () => {
  expect(pacienteValido.dni).toBe('12345678');
  expect(listaPacientes).toHaveLength(4);
});
```

### Fixtures disponibles

**Pacientes**: `pacienteValido`, `pacienteCompleto`, `pacienteInactivo`, `pacienteConNombreLargo`, `listaPacientes`, `pacienteInvalido`

**Especialistas**: `especialistaValido`, `especialistaCompleto`, `especialistaInactivo`, `especialistaPsicologo`, `especialistaPsiquiatra`, `listaEspecialistas`, `especialistaInvalido`

**Historias**: `historiaValida`, `historiaCompleta`, `historiaCerrada`, `historiaEnProceso`, `listaHistorias`, `historiaInvalida`

## Mocks

### Mock de API

```javascript
import { mockPacientesAPI } from '../tests/mocks';
import { pacienteCompleto } from '../tests/fixtures';

it('debe obtener paciente por ID', async () => {
  global.fetch = mockPacientesAPI.getById(pacienteCompleto);

  const response = await fetch('/api/pacientes/1');
  const result = await response.json();

  expect(result.success).toBe(true);
  expect(result.data).toEqual(pacienteCompleto);
});
```

**Funciones disponibles:**
- `createMockFetch(data, success)` — mock genérico
- `createMockFetchError(error)` — mock con error
- `createMockFetchNetworkError()` — mock de error de red
- `mockPacientesAPI` — mocks para endpoints de pacientes
- `mockEspecialistasAPI` — mocks para endpoints de especialistas
- `mockHistoriasAPI` — mocks para endpoints de historias

### Mock de navegación

```javascript
import { createMockGoto } from '../tests/mocks';

it('debe navegar después de crear', async () => {
  const mockGoto = createMockGoto();
  await mockGoto('/pacientes');
  expect(mockGoto).toHaveBeenCalledWith('/pacientes');
});
```

**Funciones disponibles:** `createMockGoto()`, `mockNavigation`

## Utilidades

### Test Helpers

```javascript
import { fillForm, submitForm, getFormErrors } from '../tests/utils';

it('debe llenar y enviar formulario', async () => {
  const { container } = render(PacienteForm);

  await fillForm(container, { dni: '12345678', nombres: 'Juan', apellidos: 'Pérez' });
  await submitForm(container.querySelector('form'));

  expect(getFormErrors(container)).toHaveLength(0);
});
```

**Funciones disponibles:** `fillForm`, `submitForm`, `clickElement`, `waitFor`, `sleep`, `getTextContent`, `hasClass`, `getFormErrors`, `hasInputError`, `clearForm`, `typeText`, `getInputValue`, `isButtonDisabled`

### Validators

```javascript
import { isValidDNI, getExpectedPacienteErrors } from '../tests/utils';

it('debe validar DNI', () => {
  expect(isValidDNI('12345678')).toBe(true);
  expect(isValidDNI('123')).toBe(false);
});
```

**Funciones disponibles:** `isValidDNI`, `isValidName`, `isValidEmail`, `isValidTelefono`, `isValidLength`, `isValidBirthDate`, `getExpectedPacienteErrors`, `getExpectedEspecialistaErrors`

## Ejecutar tests

```bash
# Modo watch
npm run test:unit

# Ejecución única
npm test

# Con cobertura
npm run test:unit -- --coverage
```

## Cobertura

| Componente | Fixtures | Mocks | Tests |
|---|---|---|---|
| Pacientes | 6 | API | 43 |
| Especialistas | 6 | API | 38 |
| Historias | 5 | API | 32 |
| Navegación | — | goto | — |
| Validadores | — | — | incluidos |

## Convenciones

### Nomenclatura
- Archivos: `*.spec.js` o `*.test.js`
- Describe: `'NombreComponente - Funcionalidad'`
- It: `'debe [acción esperada]'`

### Organización
- Agrupar tests relacionados con `describe()`
- Un archivo de test por componente
- Tests específicos antes de genéricos

### Fixtures y aserciones
- Usar fixtures en lugar de datos hardcodeados
- Incluir casos válidos e inválidos
- Una aserción por test cuando sea posible
- Usar matchers específicos de Vitest

### Configuración
- **Framework**: Vitest (`vite.config.js`)
- **E2E**: Playwright (Chromium) — configurado en `vite.config.js`
