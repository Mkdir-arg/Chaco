---
name: Baja de ciudadano en programa persistente
description: Permite dar de baja formal a un ciudadano de un programa persistente registrando motivo y fecha, cancelando turnos pendientes y suspendiendo el flujo activo.
type: requerimiento
---

# Baja de ciudadano en programa persistente
> Estado: CERRADO (implementado 2026-03-15)
> Fecha: 2026-03-12
> Prioridad: MEDIA
> Tipo: FEATURE

## Descripción

Los programas persistentes mantienen al ciudadano activo hasta que un operador registra la baja manualmente. Esta funcionalidad implementa ese botón de baja con todas sus consecuencias.

## Dependencias

- **US-006** Motor de flujos (para suspender la InstanciaFlujo activa)
- **US-012** Inscripción y derivación (InscripcionPrograma debe existir)

## Reglas de negocio

- Solo aplica a programas de naturaleza **persistente** — los de "un solo acto" cierran automáticamente al completar el flujo
- Solo pueden dar de baja operadores con el rol correspondiente al programa (`programaOperar`)
- Al dar de baja:
  - `InscripcionPrograma.estado` → `DADO_DE_BAJA`
  - La `InstanciaFlujo` activa → suspendida
  - Los turnos pendientes del ciudadano en ese programa → cancelados (slots liberados)
- Se registra: quién dio la baja, fecha y hora, motivo (campo obligatorio)
- La baja es irreversible desde la UI — no hay "reactivar" en esta versión
- Queda registrado en la auditoría del sistema

## Criterios de éxito

- [ ] El operador con `programaOperar` ve un botón "Dar de baja" en la vista del ciudadano dentro del programa
- [ ] Al hacer click aparece un modal con campo motivo obligatorio y confirmación (SweetAlert2)
- [ ] Al confirmar: InscripcionPrograma pasa a DADO_DE_BAJA, flujo activo se suspende, turnos pendientes se cancelan
- [ ] Se registra en auditoría: quién, cuándo, motivo
- [ ] El ciudadano ya no aparece como activo en ese programa
- [ ] Usuarios sin `programaOperar` no ven el botón de baja
