# Guía de Testing - Mental Health Predictor

Esta carpeta contiene todas las utilidades, fixtures y mocks necesarios para escribir tests en el proyecto.

## 📊 Estado actual del proyecto

- ✅ **Tests implementados**: 108 tests
- ✅ **Formularios cubiertos**: 3/3 completos
- ✅ **Infraestructura**: Fixtures, Mocks y Utilidades listas

### Tests por componente
```
✅ PacienteForm.spec.js         - 43 tests
✅ EspecialistaForm.spec.js     - 33 tests
✅ HistoriaClinicaForm.spec.js  - 32 tests
```

## Estructura

```
tests/
├── fixtures/          # Datos de prueba reutilizables
│   ├── pacientes.js
│   ├── especialistas.js
│   ├── historias.js
│   └── index.js
├── mocks/            # Funciones y servicios simulados
│   ├── api.js
│   ├── navigation.js
│   └── index.js
├── utils/            # Utilidades para tests
│   ├── test-helpers.js
│   ├── validators.js
│   └── index.js
└── README.md
```

## Fixtures

Los fixtures contienen datos de prueba predefinidos que puedes usar en tus tests.

### Uso básico

```javascript
import { describe, it, expect } from 'vitest';
import { pacienteValido, listaPacientes } from '../tests/fixtures';

describe('Paciente tests', () => {
  it('debe crear un paciente válido', () => {
    expect(pacienteValido.dni).toBe('12345678');
    expect(pacienteValido.nombres).toBe('Juan Carlos');
  });

  it('debe obtener lista de pacientes', () => {
    expect(listaPacientes).toHaveLength(4);
  });
});
```

### Fixtures disponibles

**Pacientes:**
- `pacienteValido` - Datos válidos para crear
- `pacienteCompleto` - Con ID y todos los campos
- `pacienteInactivo` - Paciente desactivado
- `pacienteConNombreLargo` - Para probar truncado
- `listaPacientes` - Array de 4 pacientes
- `pacienteInvalido` - Datos inválidos para testing

**Especialistas:**
- `especialistaValido`
- `especialistaCompleto`
- `especialistaInactivo`
- `especialistaPsicologo`
- `especialistaPsiquiatra`
- `listaEspecialistas`
- `especialistaInvalido`

**Historias:**
- `historiaValida`
- `historiaCompleta`
- `historiaCerrada`
- `historiaEnProceso`
- `listaHistorias`
- `historiaInvalida`

## Mocks

Los mocks simulan llamadas a APIs y funciones de navegación.

### Mock de API

```javascript
import { createMockFetch, mockPacientesAPI } from '../tests/mocks';
import { pacienteCompleto } from '../tests/fixtures';

it('debe obtener paciente por ID', async () => {
  // Configurar mock
  global.fetch = mockPacientesAPI.getById(pacienteCompleto);

  // Hacer petición
  const response = await fetch('/api/pacientes/1');
  const result = await response.json();

  // Verificar
  expect(result.success).toBe(true);
  expect(result.data).toEqual(pacienteCompleto);
});
```

### Mock de navegación

```javascript
import { createMockGoto } from '../tests/mocks';

it('debe navegar después de crear', async () => {
  const mockGoto = createMockGoto();

  // Usar mockGoto en tu componente
  await mockGoto('/pacientes');

  expect(mockGoto).toHaveBeenCalledWith('/pacientes');
});
```

### Funciones de mock disponibles

**API:**
- `createMockFetch(data, success)` - Mock genérico
- `createMockFetchError(error)` - Mock con error
- `createMockFetchNetworkError()` - Mock de error de red
- `mockPacientesAPI` - Mocks para endpoints de pacientes
- `mockEspecialistasAPI` - Mocks para endpoints de especialistas
- `mockHistoriasAPI` - Mocks para endpoints de historias

**Navegación:**
- `createMockGoto()` - Mock de goto de SvelteKit
- `mockNavigation` - Objeto con todos los mocks de navegación

## Utilidades

Funciones helper para simplificar la escritura de tests.

### Test Helpers

```javascript
import { fillForm, submitForm, clickElement } from '../tests/utils';

it('debe llenar y enviar formulario', async () => {
  const { container } = render(PacienteForm);

  // Llenar formulario
  await fillForm(container, {
    dni: '12345678',
    nombres: 'Juan',
    apellidos: 'Pérez'
  });

  // Enviar formulario
  const form = container.querySelector('form');
  await submitForm(form);

  // Verificar que no haya errores
  const errors = getFormErrors(container);
  expect(errors).toHaveLength(0);
});
```

### Validators

```javascript
import { isValidDNI, isValidEmail, getExpectedPacienteErrors } from '../tests/utils';

it('debe validar DNI correctamente', () => {
  expect(isValidDNI('12345678')).toBe(true);
  expect(isValidDNI('123')).toBe(false);
  expect(isValidDNI('abcd1234')).toBe(false);
});

it('debe retornar errores esperados', () => {
  const datosInvalidos = { dni: '123', nombres: '', apellidos: '' };
  const errors = getExpectedPacienteErrors(datosInvalidos);

  expect(errors.dni).toBeDefined();
  expect(errors.nombres).toBeDefined();
});
```

### Funciones disponibles

**Test Helpers:**
- `fillForm(container, data)` - Llena formulario
- `submitForm(form)` - Envía formulario
- `clickElement(element)` - Simula click
- `waitFor(condition, timeout)` - Espera condición
- `sleep(ms)` - Espera tiempo
- `getTextContent(element)` - Obtiene texto
- `hasClass(element, className)` - Verifica clase
- `getFormErrors(container)` - Obtiene errores
- `hasInputError(input)` - Verifica error en input
- `clearForm(container)` - Limpia formulario
- `typeText(input, text, delay)` - Escribe texto
- `getInputValue(container, id)` - Obtiene valor
- `isButtonDisabled(button)` - Verifica si está deshabilitado

**Validators:**
- `isValidDNI(dni)` - Valida DNI (8 dígitos)
- `isValidName(text)` - Valida nombre/apellido (solo letras)
- `isValidEmail(email)` - Valida email
- `isValidTelefono(telefono)` - Valida teléfono (9 dígitos)
- `isValidLength(text, max, min)` - Valida longitud
- `isValidBirthDate(date)` - Valida fecha de nacimiento
- `getExpectedPacienteErrors(paciente)` - Errores esperados
- `getExpectedEspecialistaErrors(especialista)` - Errores esperados

## Ejecutar tests

```bash
# Ejecutar tests en modo watch
npm run test:unit

# Ejecutar tests una vez
npm test

# Ejecutar tests con cobertura
npm run test:unit -- --coverage
```

## 📈 Cobertura de testing

| Componente | Fixtures | Mocks | Tests | Estado |
|-----------|----------|-------|-------|--------|
| Pacientes | ✅ 6 | ✅ API | ✅ 43 | Completo |
| Especialistas | ✅ 6 | ✅ API | ✅ 33 | Completo |
| Historias | ✅ 5 | ✅ API | ✅ 32 | Completo |
| Navegación | - | ✅ goto | - | Disponible |
| Validadores | - | - | ✅ | Completo |

## 🎯 Próximos pasos sugeridos

Para expandir la suite de tests:

1. **Tests de integración** - Flujos completos de usuario
2. **Tests E2E** - Ya configurado con Playwright en `vite.config.js`
3. **Tests de servicios** - `src/lib/server/services/*.spec.js`
4. **Tests de validadores Zod** - `src/lib/server/validators/*.spec.js`
5. **Tests de API endpoints** - `src/routes/api/**/*.spec.js`

## 📝 Convenciones de testing

1. **Nomenclatura**
   - Archivos: `*.spec.js` o `*.test.js`
   - Describe: `'NombreComponente - Funcionalidad'`
   - It: `'debe [acción esperada]'`

2. **Organización**
   - Agrupar tests relacionados con `describe()`
   - Un archivo de test por componente
   - Tests específicos antes de genéricos

3. **Fixtures**
   - Usar fixtures en lugar de datos hardcodeados
   - Crear fixtures realistas
   - Incluir casos válidos e inválidos

4. **Aserciones**
   - Una aserción por test cuando sea posible
   - Mensajes de error claros
   - Usar matchers específicos de Vitest

## 🔧 Configuración del proyecto

### Vitest
- **Framework**: Vitest
- **Configuración**: `vite.config.js`
- **Entornos**: Browser (Svelte) y Node (Server)

### Playwright
- **Provider**: Playwright
- **Browser**: Chromium
- **Tests de componentes**: Svelte en navegador real

## 📚 Recursos adicionales

- [Vitest Docs](https://vitest.dev/)
- [Testing Library](https://testing-library.com/)
- [Svelte Testing Guide](https://svelte.dev/docs/testing)

---
