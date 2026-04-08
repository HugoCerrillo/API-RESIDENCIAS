% =================================================================
% MOTOR DE INFERENCIA - reglas.pl
% Proyecto: Sistema Experto de Diagnóstico de Equipo de Cómputo
% =================================================================

% 1. DECLARACIONES DINÁMICAS
% Esto permite que las respuestas del usuario se almacenen en la RAM
% durante la sesión de diagnóstico.
:- dynamic respuesta/2.

% 2. CARGA DE LA BASE DE CONOCIMIENTOS
% Importa el archivo generado desde tu base de datos.
:- consult('hechos.pl').

% 3. LÓGICA DE CONTROL DE SESIÓN
% Limpia todas las respuestas previas para iniciar un nuevo diagnóstico.
limpiar_memoria :- 
    retractall(respuesta(_, _)).

% 4. MOTOR DE INFERENCIA PRINCIPAL (siguiente_paso/4)
% Esta es la regla que Flask llamará repetidamente.
% Argumentos: Tipo (PC/Laptop), Sintoma (Llave), Accion (Pregunta/Diagnóstico), Valor.

% CASO 1: Encontrar un diagnóstico exitoso
% Si encontramos una falla cuyo síntoma coincida y el usuario ya confirmó la pista.
siguiente_paso(Tipo, Sintoma, 'diagnostico', Valor) :-
    falla_info(ID, Tipo, Diagnostico, Recomendacion),
    condicion(ID, Sintoma, Pista),
    respuesta(Pista, si), % El usuario ya dijo que sí anteriormente
    !,
    atomic_list_concat([Diagnostico, ' --- SOLUCIÓN: ', Recomendacion], Valor).

% CASO 2: Sugerir la siguiente pregunta
% Busca una falla que sea viable y cuya pista aún no se haya preguntado.
siguiente_paso(Tipo, Sintoma, 'pregunta', Pista) :-
    falla_info(ID, Tipo, _, _),
    condicion(ID, Sintoma, Pista),
    not(respuesta(Pista, _)), % No se ha preguntado aún
    falla_viable(ID),          % La falla no ha sido descartada por otras respuestas
    !.

% CASO 3: Fin del conocimiento
% Si ya no hay mas que preguntar y no se hallo diagnóstico.
siguiente_paso(_, _, 'finalizado', 'No se encontro un diagnóstico exacto en la base de datos actual.').


% 5. REGLAS AUXILIARES DE VALIDACIÓN

% Una falla es viable si NO hay ninguna pista asociada que el usuario haya respondido como 'no'.
falla_viable(ID) :-
    not((
        condicion(ID, _, Pista),
        respuesta(Pista, no)
    )).

% 6. REGLA DE DIAGNÓSTICOS MÚLTIPLES (Opcional para reportes)
% Devuelve una lista de todos los diagnósticos que coinciden con las respuestas actuales.
listar_diagnosticos_posibles(Tipo, Sintoma, Lista) :-
    findall(D, (
        falla_info(ID, Tipo, D, _),
        condicion(ID, Sintoma, P),
        respuesta(P, si)
    ), Lista).