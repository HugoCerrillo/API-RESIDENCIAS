% Declaraciones dinamicas
% almacenamos las respuestas del usuario durante la sesion de diagnostico.
:- dynamic respuesta/2.

% Carga de la base de conocimientos
% Importa el archivo generado desde tu base de datos.
:- consult('hechos.pl').
    
% Control de sesion
% limpiamos todas las respuestas previas para iniciar un nuevo diagnostico.
limpiar_memoria :- 
    retractall(respuesta(_, _)).

% Motor de inferencia principal
% Esta es la regla que Flask llamará repetidamente.
% Argumentos: Tipo (PC/Laptop), Sintoma (Llave), Accion (Pregunta/Diagnóstico), Valor.

% CASO 1: Encontrar un diagnóstico exitoso
% Si encontramos una falla cuyo sintoma coincida y el usuario ya confirmo la pista
siguiente_paso(Tipo, Sintoma, 'diagnostico', Valor) :-
    falla_info(ID, Tipo, Diagnostico, Recomendacion), % sirve para obtener el diagnostico y la recomendacion
    condicion(ID, Sintoma, Pista), % sirve para obtener la pista
    respuesta(Pista, si), % sirve para verificar si el usuario ya dijo que si a la pista
    !,
    atomic_list_concat([Diagnostico, ' --- SOLUCIÓN: ', Recomendacion], Valor).

% CASO 2: Sugerir la siguiente pregunta
% Busca una falla que sea viable y cuya pista aún no se haya preguntado.
siguiente_paso(Tipo, Sintoma, 'pregunta', Pista) :-
    falla_info(ID, Tipo, _, _), % sirve para obtener el diagnostico y la recomendacion
    condicion(ID, Sintoma, Pista), % sirve para obtener la pista
    not(respuesta(Pista, _)), % verificar si el usuario ya dijo que no a la pista
    falla_viable(ID),          % verificar si la falla es viable
    !.

% CASO 3: Fin del conocimiento (no logro encontrar el diagnostico)
% Si ya no hay mas que preguntar y no se hallo diagnóstico.
siguiente_paso(_, _, 'finalizado', 'No se encontro un diagnóstico exacto en la base de datos actual.').


% 5. validar si una falla es viable
% Una falla es viable si NO hay ninguna pista asociada que el usuario haya respondido como 'no'.
falla_viable(ID) :-
    not((
        condicion(ID, _, Pista), % sirve para obtener la pista
        respuesta(Pista, no) % sirve para verificar si el usuario ya dijo que no a la pista
    )).
