% definicion de predicados 
% falla_info(ID, Equipo, Diagnostico, Recomendacion): Información general 
% almacenamos el ID de la falla, el tipo de equipo, el diagnostico y la recomendacion


% falla_categoria(ID, Categoria): funciona tambien para filtrados
% almacenamos el ID de fala con la categoria


% condicion(ID, Sintoma, Pregunta): Relación logica que se debe cumplir para que se presente la falla
% almacenamos el ID de la falla con el sintoma y la pregunta



% --- hechos.pl: Información de Diagnóstico ---
% PC (1-50)
falla_info(1, 'PC', 'Falla en cable/suministro', 'Probar otro cable o toma.').
falla_info(2, 'PC', 'Fuente bloqueada por corto', 'Desconectar 1 min y descargar.').
falla_info(3, 'PC', 'Falla conector ATX 12V', 'Verificar conector 4/8 pines CPU.').
falla_info(4, 'PC', 'Botón gabinete dañado', 'Reemplazar botón de encendido.').
falla_info(5, 'PC', 'Corto interno en Fuente', 'Reemplazar Fuente de Poder.').
falla_info(6, 'PC', 'Sobrecalentamiento Fuente', 'Limpiar o cambiar ventilador.').
falla_info(7, 'PC', 'Corto en puertos USB frontales', 'Desconectar panel frontal.').
falla_info(8, 'PC', 'Flujo de aire insuficiente', 'Agregar ventiladores de chasis.').
falla_info(9, 'PC', 'Capacitores degradados', 'Reemplazar fuente de poder.').
falla_info(10, 'PC', 'Falso contacto cable poder', 'Ajustar cable o cambiar entrada.').
falla_info(11, 'PC', 'Protección térmica instantánea', 'Reasentar y poner pasta térmica.').
falla_info(12, 'PC', 'Desgaste físico de placa', 'Reparación o cambio de placa.').
falla_info(13, 'PC', 'Interruptor desactivado', 'Colocar interruptor en I.').
falla_info(14, 'PC', 'Configuración errónea', 'Ajustar a 115v o 230v.').
falla_info(15, 'PC', 'Sobrecarga línea 12V', 'Fuente de mayor vataje.').
falla_info(16, 'PC', 'Falla equipo protección', 'Probar directo a la pared.').
falla_info(17, 'PC', 'Corto por objeto metálico', 'Retirar tornillo y limpiar.').
falla_info(18, 'PC', 'Degradación térmica', 'Mantenimiento preventivo.').
falla_info(19, 'PC', 'Falso contacto principal', 'Presionar hasta escuchar clic.').
falla_info(20, 'PC', 'BIOS no inicializa', 'Reemplazar pila y reset CMOS.').
falla_info(21, 'PC', 'Error lectura RPM', 'Conectar en CPU_FAN.').
falla_info(22, 'PC', 'Fuente insuficiente para GPU', 'Fuente certificada 80 Plus.').
falla_info(23, 'PC', 'Corto por falta separadores', 'Instalar separadores (standoffs).').
falla_info(24, 'PC', 'Combustión de VRMs', 'Declarar equipo fuera servicio.').
falla_info(25, 'PC', 'Señal de reset constante', 'Desconectar cable Reset SW.').
falla_info(26, 'PC', 'Riesgo de incendio', 'Usar conectores directos.').
falla_info(27, 'PC', 'Fatiga de material cableado', 'Acomodar cables sin presión.').
falla_info(28, 'PC', 'Fuga o falta de tierra', 'Revisar instalación eléctrica.').
falla_info(29, 'PC', 'Arco eléctrico en entrada', 'Limpiar o cambiar cable poder.').
falla_info(30, 'PC', 'Falla mecánica ventilador', 'Lubricar o cambiar fan CPU.').
falla_info(31, 'PC', 'Corto por condensación', 'Secar y limpiar con isopropílico.').
falla_info(32, 'PC', 'Voltaje insuficiente RAM', 'Ajustar BIOS (XMP).').
falla_info(33, 'PC', 'Exceso corriente CPU', 'Revisar si CPU está en corto.').
falla_info(34, 'PC', 'Falla interna conexión', 'Ajustar cables de fuente modular.').
falla_info(35, 'PC', 'Conductividad por polvo', 'Limpiar slots con aire.').
falla_info(36, 'PC', 'Desalineación pines PCIe', 'Asegurar tornillos de GPU.').
falla_info(37, 'PC', 'Ahogamiento térmico', 'Limpiar filtros de aire.').
falla_info(38, 'PC', 'Impedancia alta capacitores', 'Alcanzar temperatura ambiente.').
falla_info(39, 'PC', 'Cierre circuito constante', 'Limpiar botón con alcohol.').
falla_info(40, 'PC', 'Corto bus energía CPU', 'Enderezar pines o cambiar placa.').
falla_info(41, 'PC', 'Error ensamble térmico', 'Retirar plástico y reensamblar.').
falla_info(42, 'PC', 'Protección OVP activa', 'Desconectar periféricos.').
falla_info(43, 'PC', 'Caída voltaje línea SATA', 'Cambiar rama cables fuente.').
falla_info(44, 'PC', 'Pinout incompatible', 'Usar solo cables originales.').
falla_info(45, 'PC', 'Falla voltaje puente norte', 'Mejorar disipación chipset.').
falla_info(46, 'PC', 'Cortos por fauna', 'Limpieza y control plagas.').
falla_info(47, 'PC', 'Sensor placa dañado', 'Actualizar BIOS o reparar.').
falla_info(48, 'PC', 'Sobrecarga línea 5V', 'Desconectar estética LED.').
falla_info(49, 'PC', 'Mal contacto eléctrico', 'Cambiar fuente o conector.').
falla_info(50, 'PC', 'Daño circuito standby', 'Probar con fuente conocida.').

% Laptop (51-100)
falla_info(51, 'Laptop', 'Corto grave en Motherboard', 'Revisar Mosfets de entrada.').
falla_info(52, 'Laptop', 'Batería en cortocircuito', 'Usar solo con cargador.').
falla_info(53, 'Laptop', 'Falla ID cargador', 'Reemplazar por original.').
falla_info(54, 'Laptop', 'Batería muerta', 'Reemplazar batería interna.').
falla_info(55, 'Laptop', 'Obstrucción por pelusa', 'Limpiar ventilación interna.').
falla_info(56, 'Laptop', 'Código error batería', 'Consultar manual de marca.').
falla_info(57, 'Laptop', 'Jack de carga quemado', 'Cambiar cable Jack interno.').
falla_info(58, 'Laptop', 'Corto en cable Flex', 'Revisar/cambiar flexor video.').
falla_info(59, 'Laptop', 'Flexión de placa madre', 'Evitar cargarla de esquinas.').
falla_info(60, 'Laptop', 'Cargador en corto', 'Cambiar cargador de inmediato.').
falla_info(61, 'Laptop', 'Corrosión por humedad', 'Limpieza isopropílica total.').
falla_info(62, 'Laptop', 'Fan desgastado', 'Reemplazar fan de laptop.').
falla_info(63, 'Laptop', 'Ciclo energía bloqueado', 'Resetear controlador (EC).').
falla_info(64, 'Laptop', 'Soldadura desprendida', 'Resoldar o cambiar puerto.').
falla_info(65, 'Laptop', 'Celda muerta', 'Calibrar o cambiar batería.').
falla_info(66, 'Laptop', 'Batería bajo umbral', 'Carga lenta de reactivación.').
falla_info(67, 'Laptop', 'Asfixia térmica', 'Usar en superficie plana.').
falla_info(68, 'Laptop', 'Falla secuencia poder', 'Drenado de energía (Hard reset).').
falla_info(69, 'Laptop', 'Corto en puerto de video', 'Revisar integridad HDMI.').
falla_info(70, 'Laptop', 'Energía insuficiente', 'Usar vataje correcto.').
falla_info(71, 'Laptop', 'Riesgo explosión', 'Retirar batería con cuidado.').
falla_info(72, 'Laptop', 'Caída voltaje línea 5V', 'Probar sin disco instalado.').
falla_info(73, 'Laptop', 'Firmware no reconocido', 'Actualizar BIOS y drivers.').
falla_info(74, 'Laptop', 'Voltaje inestable', 'Usar cargador certificado.').
falla_info(75, 'Laptop', 'Disipador saturado', 'Mantenimiento interno.').
falla_info(76, 'Laptop', 'Obstrucción física', 'Limpiar con aguja y alcohol.').
falla_info(77, 'Laptop', 'Consumo inestable GPU', 'Reinstalar drivers oficiales.').
falla_info(78, 'Laptop', 'Falla inverter/backlight', 'Probar con monitor externo.').
falla_info(79, 'Laptop', 'Falla regulador luz', 'Revisar capacitores LCD.').
falla_info(80, 'Laptop', 'Corto en bobinas placa', 'Reparación microelectrónica.').
falla_info(81, 'Laptop', 'Módulo red en corto', 'Reemplazar tarjeta M.2 Wifi.').
falla_info(82, 'Laptop', 'Falla continuidad', 'Reemplazar cargador completo.').
falla_info(83, 'Laptop', 'Standby insuficiente', 'Revisar regulador de placa.').
falla_info(84, 'Laptop', 'Falla sensor térmico', 'Cambiar ventilador.').
falla_info(85, 'Laptop', 'Componente interno flojo', 'Reasentar RAM/SSD.').
falla_info(86, 'Laptop', 'Desgaste químico', 'Revisar desgaste con software.').
falla_info(87, 'Laptop', 'Teclado dañado', 'Probar puenteando pines.').
falla_info(88, 'Laptop', 'Corto lector tarjetas', 'Desactivar en BIOS.').
falla_info(89, 'Laptop', 'Corrosión por humedad', 'Limpiar con cepillo duro.').
falla_info(90, 'Laptop', 'Apagado térmico', 'Limpieza y pads térmicos.').
falla_info(91, 'Laptop', 'Jack con holgura', 'Cambiar puerto carga interno.').
falla_info(92, 'Laptop', 'Pila CMOS agotada', 'Cambiar pila interna.').
falla_info(93, 'Laptop', 'Ruido eléctrico USB', 'Probar sin periféricos.').
falla_info(94, 'Laptop', 'Falla IC Charging', 'Reparación nivel componente.').
falla_info(95, 'Laptop', 'Deformación o sensor', 'Enfriar en lugar sombreado.').
falla_info(96, 'Laptop', 'Celda desbalanceada', 'Cambiar batería por nueva.').
falla_info(97, 'Laptop', 'Falla memoria integrada', 'Cambiar placa madre.').
falla_info(98, 'Laptop', 'BIOS corrupto', 'Reset CMOS profundo.').
falla_info(99, 'Laptop', 'Corto en bisagra', 'Reparar cableado bisagra.').
falla_info(100, 'Laptop', 'Falla interna tras Jack', 'Diagnóstico etapa potencia.').

% --- hechos.pl: Lógica de Preguntas ---

condicion(1, no_enciende, '¿LED de fuente atrás encendido?').
condicion(2, no_enciende, '¿Escucha un clic al presionar?').
condicion(3, no_enciende, '¿Ventiladores giran sin pitidos?').
condicion(4, no_enciende, '¿Enciende puenteando pines?').
condicion(5, no_enciende, '¿Huele a quemado en la fuente?').
condicion(6, se_apaga_solo, '¿Fan de fuente se detiene?').
condicion(7, se_apaga_solo, '¿Apaga al conectar algo USB?').
condicion(8, se_apaga_solo, '¿Gabinete sin ventilación extra?').
condicion(9, se_apaga_solo, '¿Fuente emite zumbido agudo?').
condicion(10, reinicia_solo, '¿Reinicia al mover el equipo?').
condicion(11, enciende_y_apaga, '¿Disipador del CPU está flojo?').
condicion(12, enciende_y_apaga, '¿Capacitadores inflados en placa?').
condicion(13, no_enciende, '¿Interruptor trasero en O?').
condicion(14, no_enciende, '¿Selector voltaje incorrecto?').
condicion(15, se_apaga_solo, '¿Apaga al usar muchos discos?').
condicion(16, no_enciende, '¿Regulador externo hace ruido?').
condicion(17, enciende_y_apaga, '¿Tornillo suelto sobre placa?').
condicion(18, se_apaga_solo, '¿Pasta térmica muy antigua?').
condicion(19, reinicia_solo, '¿Conector 24 pines flojo?').
condicion(20, no_enciende, '¿Pila BIOS (CR2032) sin carga?').
condicion(21, enciende_y_apaga, '¿Fan en puerto incorrecto?').
condicion(22, se_apaga_solo, '¿Tiene GPU de gama alta?').
condicion(23, no_enciende, '¿Placa toca metal del chasis?').
condicion(24, no_enciende, '¿Humo saliendo de placa?').
condicion(25, reinicia_solo, '¿Cable de reset pegado?').
condicion(26, no_enciende, '¿Usa adaptadores Molex-SATA?').
condicion(27, se_apaga_solo, '¿Cables internos muy tensos?').
condicion(28, no_enciende, '¿Chasis da toques eléctricos?').
condicion(29, enciende_y_apaga, '¿Chisporroteo en conector?').
condicion(30, se_apaga_solo, '¿Fan CPU gira muy lento?').
condicion(31, no_enciende, '¿Humedad visible en equipo?').
condicion(32, reinicia_solo, '¿Frecuencia RAM muy alta?').
condicion(33, no_enciende, '¿Cable 8 pines CPU quemado?').
condicion(34, se_apaga_solo, '¿Cables modulares flojos?').
condicion(35, no_enciende, '¿Polvo excesivo en slots RAM?').
condicion(36, enciende_y_apaga, '¿GPU mal atornillada?').
condicion(37, se_apaga_solo, '¿Filtros de polvo tapados?').
condicion(38, no_enciende, '¿Ambiente frío extremo?').
condicion(39, reinicia_solo, '¿Botón encendido pegado?').
condicion(40, no_enciende, '¿Pines de socket doblados?').
condicion(41, se_apaga_solo, '¿Plástico en disipador puesto?').
condicion(42, no_enciende, '¿Fuente pita agudo?').
condicion(43, reinicia_solo, '¿Ruido de encendido en disco?').
condicion(44, no_enciende, '¿Cables de otra fuente usados?').
condicion(45, se_apaga_solo, '¿Chipset quema al tacto?').
condicion(46, no_enciende, '¿Rastros insectos dentro?').
condicion(47, enciende_y_apaga, '¿BIOS marca Overvoltage?').
condicion(48, se_apaga_solo, '¿Usa tiras LED conectadas?').
condicion(49, no_enciende, '¿Pines ATX negros/quemados?').
condicion(50, se_apaga_solo, '¿Tras un apagón previo?').
condicion(51, no_enciende, '¿LED cargador apaga al conectar?').
condicion(52, no_enciende, '¿Enciende sin batería?').
condicion(53, no_enciende, '¿Pin central cargador roto?').
condicion(54, se_apaga_solo, '¿Apaga al quitar cargador?').
condicion(55, se_apaga_solo, '¿Base se siente muy caliente?').
condicion(56, no_enciende, '¿LED parpadea naranja/blanco?').
condicion(57, no_enciende, '¿Huele quemado en Jack carga?').
condicion(58, se_apaga_solo, '¿Apaga al mover la pantalla?').
condicion(59, se_apaga_solo, '¿Apaga al levantarla de lado?').
condicion(60, no_carga, '¿Cargador hace tic-tic-tic?').
condicion(61, no_enciende, '¿Líquido derramado en teclado?').
condicion(62, se_apaga_solo, '¿Ventilador hace ruido mecánico?').
condicion(63, no_enciende, '¿Usó botón reset (orificio)?').
condicion(64, no_carga, '¿Puerto USB-C carga flojo?').
condicion(65, se_apaga_solo, '¿Batería cae de 100% a 0%?').
condicion(66, no_enciende, '¿Guardada meses descargada?').
condicion(67, se_apaga_solo, '¿Usa en cama o sillón?').
condicion(68, no_enciende, '¿Teclado prende pero no imagen?').
condicion(69, se_apaga_solo, '¿Apaga al conectar HDMI?').
condicion(70, no_carga, '¿Cargador de menor vataje?').
condicion(71, no_enciende, '¿Batería está hinchada?').
condicion(72, enciende_y_apaga, '¿Disco duro intenta girar?').
condicion(73, se_apaga_solo, '¿Error Internal Battery?').
condicion(74, no_enciende, '¿Usa cargador universal barato?').
condicion(75, se_apaga_solo, '¿Teclado quema al tacto?').
condicion(76, no_carga, '¿Pelusa dentro de Jack carga?').
condicion(77, reinicia_solo, '¿Pantallazo azul en video?').
condicion(78, no_enciende, '¿Pantalla parpadea 1 segundo?').
condicion(79, se_apaga_solo, '¿Apaga con brillo al máximo?').
condicion(80, no_enciende, '¿Zumbido dentro de laptop?').
condicion(81, se_apaga_solo, '¿Apaga al usar Bluetooth/Wifi?').
condicion(82, no_carga, '¿Cable cargador mordido?').
condicion(83, no_enciende, '¿Luz encendido brilla tenue?').
condicion(84, se_apaga_solo, '¿Fan no gira nunca?').
condicion(85, reinicia_solo, '¿Recibió golpe reciente?').
condicion(86, no_carga, '¿Dice Conectado sin cargarse?').
condicion(87, no_enciende, '¿Botón encendido en teclado?').
condicion(88, se_apaga_solo, '¿Apaga al insertar SD?').
condicion(89, no_enciende, '¿Contactos batería sulfatados?').
condicion(90, se_apaga_solo, '¿Apaga al llegar a 90C?').
condicion(91, no_carga, '¿Carga se corta al vibrar?').
condicion(92, no_enciende, '¿BIOS marca Low Voltage?').
condicion(93, se_apaga_solo, '¿Base enfriadora USB mala?').
condicion(94, no_carga, '¿Detecta pero no sube %?').
condicion(95, no_enciende, '¿Expuesta al sol directo?').
condicion(96, se_apaga_solo, '¿Apaga bajo 20% batería?').
condicion(97, reinicia_solo, '¿RAM soldada falla con carga?').
condicion(98, no_enciende, '¿Fan al máximo al prender?').
condicion(99, se_apaga_solo, '¿Cable pantalla pinchado?').
condicion(100, no_enciende, '¿Cargador da voltaje correcto?').


% --- Información de Diagnóstico (101-200)  segunda cateogira de la tabla---

falla_info(101, 'PC', 'Falla de sectores críticos', 'Escanear con CrystalDiskInfo.').
falla_info(102, 'PC', 'Cable SATA defectuoso', 'Reemplazar cable de datos.').
falla_info(103, 'PC', 'Prioridad de booteo errónea', 'Configurar HDD/SSD como primero.').
falla_info(104, 'PC', 'MBR/GPT Corrupto', 'Reparar inicio con CMD de Windows.').
falla_info(105, 'PC', 'SSD en modo lectura', 'Respaldar datos y cambiar unidad.').
falla_info(106, 'PC', 'Sobrecalentamiento Disco', 'Mejorar flujo de aire en bahías.').
falla_info(107, 'PC', 'Falta de driver AHCI', 'Cargar driver durante instalación.').
falla_info(108, 'PC', 'Voltaje insuficiente SATA', 'Cambiar conector de energía.').
falla_info(109, 'PC', 'Vibración excesiva', 'Ajustar tornillos de montaje.').
falla_info(110, 'PC', 'Puerto SATA de placa dañado', 'Cambiar a otro puerto SATA disponible.').
falla_info(111, 'PC', 'Módulo RAM mal sentado', 'Reasentar módulo hasta el clic.').
falla_info(112, 'PC', 'Falla de direccionamiento', 'Probar módulos por separado.').
falla_info(113, 'PC', 'Incompatibilidad de BUS', 'Ajustar frecuencia en BIOS.').
falla_info(114, 'PC', 'Voltaje de RAM bajo', 'Subir voltaje DRAM (con cuidado).').
falla_info(115, 'PC', 'Slot de memoria sucio', 'Limpiar con aire comprimido.').
falla_info(116, 'PC', 'Perfiles XMP inestables', 'Desactivar XMP y usar base.').
falla_info(117, 'PC', 'Error de paridad', 'Cambiar módulo de memoria.').
falla_info(118, 'PC', 'Mezcla de densidades', 'Usar módulos de misma capacidad.').
falla_info(119, 'PC', 'Estática en contactos', 'Limpiar con goma de borrar blanca.').
falla_info(120, 'PC', 'Controlador de memoria CPU', 'Bajar frecuencia o cambiar CPU.').
falla_info(121, 'PC', 'Pasta térmica seca', 'Limpiar y aplicar nueva pasta.').
falla_info(122, 'PC', 'Bomba de AIO fallida', 'Reemplazar refrigeración líquida.').
falla_info(123, 'PC', 'Burbujas en el bloque', 'Girar gabinete para purgar aire.').
falla_info(124, 'PC', 'Pin doblado en placa', 'Enderezar pin con lupa y aguja.').
falla_info(125, 'PC', 'Overclock inestable', 'Resetear CMOS a valores de fábrica.').
falla_info(126, 'PC', 'VRMs sin disipación', 'Agregar disipadores o flujo aire.').
falla_info(127, 'PC', 'Socket sucio (LGA)', 'Limpiar con alcohol isopropílico.').
falla_info(128, 'PC', 'Throttling por BIOS', 'Actualizar BIOS de la placa.').
falla_info(129, 'PC', 'Montaje excesivo presión', 'Aflojar ligeramente tornillos cooler.').
falla_info(130, 'PC', 'CPU no soportado', 'Verificar lista compatibilidad (QVL).').
falla_info(131, 'PC', 'GPU mal alimentada', 'Conectar cables PCIe independientes.').
falla_info(132, 'PC', 'Artifactos por calor', 'Cambiar pads térmicos de GPU.').
falla_info(133, 'PC', 'VRAM defectuosa', 'Bajar reloj de memoria (Afterburner).').
falla_info(134, 'PC', 'Driver corrupto', 'Reinstalar usando DDU (Clean Install).').
falla_info(135, 'PC', 'Slot PCIe x16 dañado', 'Probar en segundo slot PCIe.').
falla_info(136, 'PC', 'Versión de firmware GPU', 'Flashear vBIOS oficial.').
falla_info(137, 'PC', 'Sag (Pandeo) de GPU', 'Instalar soporte de tarjeta.').
falla_info(138, 'PC', 'Conflicto de IRQ', 'Cambiar de posición tarjetas PCIe.').
falla_info(139, 'PC', 'Cable DisplayPort malo', 'Probar con cable certificado.').
falla_info(140, 'PC', 'Falla de capacitores GPU', 'Reparación electrónica requerida.').
falla_info(141, 'PC', 'Fuga de corriente chasis', 'Revisar polo a tierra edificio.').
falla_info(142, 'PC', 'Corto en botón Reset', 'Desconectar cable RESET_SW.').
falla_info(143, 'PC', 'Chipset sobrecalentado', 'Mejorar ventilación frontal.').
falla_info(144, 'PC', 'Pila CMOS agotada', 'Cambiar pila CR2032.').
falla_info(145, 'PC', 'Sensor de intrusión', 'Desactivar Chassis Intrusion en BIOS.').
falla_info(146, 'PC', 'BIOS Corrupto (Dual BIOS)', 'Activar BIOS de respaldo.').
falla_info(147, 'PC', 'Pistas de placa cortadas', 'Puenteo de pistas (Nivel experto).').
falla_info(148, 'PC', 'Humedad en slots', 'Secar y usar limpia contactos.').
falla_info(149, 'PC', 'Standoffs mal puestos', 'Reinstalar separadores de placa.').
falla_info(150, 'PC', 'Incompatibilidad de marca', 'Probar componentes de otra marca.').
falla_info(151, 'Laptop', 'HDD con brazo trabado', 'Reemplazar por SSD obligatoriamente.').
falla_info(152, 'Laptop', 'Flex SATA de laptop roto', 'Cambiar cable flex interno disco.').
falla_info(153, 'Laptop', 'Caddy de HDD flojo', 'Ajustar tornillos de bahía.').
falla_info(154, 'Laptop', 'Sensor G de caída activo', 'Desactivar protección de disco.').
falla_info(155, 'Laptop', 'SSD M.2 sobrecalentado', 'Poner pad térmico contra chasis.').
falla_info(156, 'Laptop', 'Bitlocker bloqueado', 'Ingresar clave de recuperación.').
falla_info(157, 'Laptop', 'Tabla de partición RAW', 'Recuperar con TestDisk.').
falla_info(158, 'Laptop', 'Firmware de SSD desactualizado', 'Actualizar desde web fabricante.').
falla_info(159, 'Laptop', 'Consumo excesivo disco', 'Revisar procesos de telemetría.').
falla_info(160, 'Laptop', 'Ruido de click constante', 'Falla mecánica inminente (Cambiar).').
falla_info(161, 'Laptop', 'RAM DDR incompatible', 'Verificar si es DDR3L o DDR3.').
falla_info(162, 'Laptop', 'Slot de RAM oxidado', 'Limpiar con cepillo y alcohol.').
falla_info(163, 'Laptop', 'Memoria soldada dañada', 'Deshabilitar slot o cambio placa.').
falla_info(164, 'Laptop', 'Falla de bus de datos', 'Limpiar contactos CPU (si es removible).').
falla_info(165, 'Laptop', 'Latencias incompatibles', 'Usar pares iguales de memorias.').
falla_info(166, 'Laptop', 'Static Buildup', 'Drenar energía (Boton 30 seg).').
falla_info(167, 'Laptop', 'Voltaje inestable RAM', 'Probar con otro cargador original.').
falla_info(168, 'Laptop', 'Módulo de mucha densidad', 'Revisar máximo soportado por BIOS.').
falla_info(169, 'Laptop', 'Ranking de memoria (1R/2R)', 'Cambiar a módulos Single Rank.').
falla_info(170, 'Laptop', 'Error SPD', 'Reprogramar SPD o cambiar módulo.').
falla_info(171, 'Laptop', 'Pelusa en el radiador', 'Limpieza profunda de rejillas.').
falla_info(172, 'Laptop', 'Fan con eje desviado', 'Cambiar ventilador (No lubricar).').
falla_info(173, 'Laptop', 'Pipe de cobre perforado', 'Cambiar sistema de disipación.').
falla_info(174, 'Laptop', 'Software de control fan', 'Desinstalar bloatware de marca.').
falla_info(175, 'Laptop', 'Pads térmicos resecos', 'Reemplazar por pads de alta calidad.').
falla_info(176, 'Laptop', 'Uso en superficies blandas', 'Usar siempre en mesa rígida.').
falla_info(177, 'Laptop', 'Modo de ahorro térmico', 'Cambiar plan de energía a Alto.').
falla_info(178, 'Laptop', 'Malware de minería', 'Escanear con Malwarebytes.').
falla_info(179, 'Laptop', 'Obstrucción filtro base', 'Retirar polvo acumulado en base.').
falla_info(180, 'Laptop', 'Sensor térmico descalibrado', 'Actualizar Firmware de Sistema.').
falla_info(181, 'Laptop', 'Panel LCD con presión', 'Revisar que nada presione tapa.').
falla_info(182, 'Laptop', 'Inverter fallando', 'Cambiar placa inverter de pantalla.').
falla_info(183, 'Laptop', 'Cable Flex de video flojo', 'Reasentar conector tras pantalla.').
falla_info(184, 'Laptop', 'Backlight LED agotado', 'Cambiar panel completo.').
falla_info(185, 'Laptop', 'Imán de cierre pegado', 'Limpiar zona de reposamuñecas.').
falla_info(186, 'Laptop', 'Resolución no soportada', 'Resetear drivers de video (Win+B).').
falla_info(187, 'Laptop', 'Driver Intel/AMD conflicto', 'Instalar driver desde web OEM.').
falla_info(188, 'Laptop', 'Falla de refresco (Hz)', 'Bajar de 144Hz a 60Hz.').
falla_info(189, 'Laptop', 'Píxeles muertos', 'Intentar software de reactivación.').
falla_info(190, 'Laptop', 'Interferencia electromagnética', 'Alejar laptop de motores/bocinas.').
falla_info(191, 'Laptop', 'Cargador genérico ruido', 'Cambiar a cargador con ferrita.').
falla_info(192, 'Laptop', 'Toma de pared sin tierra', 'Cambiar de enchufe.').
falla_info(193, 'Laptop', 'Filtro de audio dañado', 'Cambiar jack de audio combo.').
falla_info(194, 'Laptop', 'Driver Realtek erróneo', 'Usar High Definition Audio Generic.').
falla_info(195, 'Laptop', 'Membrana teclado pegada', 'Cambiar teclado completo.').
falla_info(196, 'Laptop', 'Touchpad deshabilitado', 'Activar con tecla de función (Fn).').
falla_info(197, 'Laptop', 'Wifi bloqueado por switch', 'Activar interruptor físico Wifi.').
falla_info(198, 'Laptop', 'Antenas Wifi desconectadas', 'Revisar cables sobre tarjeta M.2.').
falla_info(199, 'Laptop', 'BIOS desactualizada', 'Flash BIOS a última versión.').
falla_info(200, 'Laptop', 'Carcasa presionando placa', 'Aflojar un poco tornillos base.').

% --- hechos.pl: Lógica de Preguntas (101-200) ---

condicion(101, disco_lento, '¿Escucha ruidos metálicos?').
condicion(102, disco_no_detectado, '¿Cambió el cable SATA recientemente?').
condicion(103, no_bootea, '¿Aparece error No Boot Device?').
condicion(104, no_bootea, '¿Dice error MBR Missing?').
condicion(105, disco_lento, '¿No deja borrar archivos?').
condicion(106, se_traba, '¿El disco quema al tocarlo?').
condicion(107, pantallazo_azul, '¿Ocurre al instalar Windows?').
condicion(108, disco_no_detectado, '¿Gira el motor del disco?').
condicion(109, ruido_extraño, '¿Gabinete vibra mucho?').
condicion(110, disco_no_detectado, '¿BIOS reconoce otros discos?').
condicion(111, pitidos_al_arrancar, '¿Son 3 pitidos largos?').
condicion(112, pantallazo_azul, '¿Error dice Memory Management?').
condicion(113, reinicia_solo, '¿Puso memorias de distinta marca?').
condicion(114, se_traba, '¿Usa memorias de alto rendimiento?').
condicion(115, no_da_imagen, '¿Equipo estuvo guardado tiempo?').
condicion(116, pantallazo_azul, '¿Activó XMP recientemente?').
condicion(117, se_traba, '¿Código error WHEA_UNCORRECTABLE?').
condicion(118, no_da_imagen, '¿Mezcló 4GB con 8GB?').
condicion(119, no_da_imagen, '¿Slots tienen polvo visible?').
condicion(120, se_traba, '¿Solo falla en procesos pesados?').
condicion(121, se_apaga_solo, '¿Temperatura CPU sube a 90C?').
condicion(122, ruido_extraño, '¿Escucha burbujeo constante?').
condicion(123, se_apaga_solo, '¿Mangueras vibran mucho?').
condicion(124, no_enciende, '¿Quitó el procesador hoy?').
condicion(125, reinicia_solo, '¿Hizo overclock manual?').
condicion(126, se_apaga_solo, '¿VRMs huelen a ozono?').
condicion(127, no_da_imagen, '¿Pasta térmica cayó en socket?').
condicion(128, se_traba, '¿CPU corre a mínima velocidad?').
condicion(129, no_da_imagen, '¿Apretó mucho el disipador?').
condicion(130, no_enciende, '¿Procesador es de nueva gen?').
condicion(131, se_apaga_solo, '¿GPU requiere 2 conectores?').
condicion(132, imagen_distorsionada, '¿Ve rayas de colores (artifacts)?').
condicion(133, se_traba, '¿Falla al abrir juegos?').
condicion(134, pantalla_negra, '¿Instaló drivers ayer?').
condicion(135, no_da_imagen, '¿Tarjeta GPU está chueca?').
condicion(136, pantalla_negra, '¿Intentó flashear la GPU?').
condicion(137, imagen_distorsionada, '¿Tarjeta es muy pesada?').
condicion(138, se_traba, '¿Tiene muchas placas PCIe?').
condicion(139, sin_señal, '¿Usa cable muy largo?').
condicion(140, no_da_imagen, '¿Huele a quemado cerca de GPU?').
condicion(141, no_enciende, '¿Gabinete le da toques?').
condicion(142, reinicia_solo, '¿Reinicia sin aviso previo?').
condicion(143, se_traba, '¿Sur de placa está muy caliente?').
condicion(144, no_guarda_hora, '¿Hora de Windows se atrasa?').
condicion(145, no_bootea, '¿Mensaje de Case Intrusion?').
condicion(146, no_enciende, '¿Falló actualización de BIOS?').
condicion(147, no_enciende, '¿Rayó la placa con desarmador?').
condicion(148, no_da_imagen, '¿Hubo derrame de líquido?').
condicion(149, no_enciende, '¿Placa toca directo el metal?').
condicion(150, se_traba, '¿Hardware es muy viejo y nuevo?').
condicion(151, laptop_lenta, '¿Escucha clics bajo el teclado?').
condicion(152, no_detecta_disco, '¿Laptop recibió un golpe?').
condicion(153, ruido_extraño, '¿Siente algo suelto dentro?').
condicion(154, laptop_lenta, '¿Se traba al mover la laptop?').
condicion(155, laptop_lenta, '¿Base está caliente bajo disco?').
condicion(156, no_bootea, '¿Pide clave azul de 48 dígitos?').
condicion(157, no_detecta_disco, '¿Aparece Operating System Not Found?').
condicion(158, pantallazo_azul, '¿SSD es de marca económica?').
condicion(159, bateria_dura_poco, '¿Luz de disco siempre brilla?').
condicion(160, ruido_extraño, '¿Suena como un reloj viejo?').
condicion(161, no_da_imagen, '¿Puso RAM nueva hoy?').
condicion(162, no_da_imagen, '¿Contactos se ven verdosos?').
condicion(163, pantallazo_azul, '¿Memoria es integrada (onboard)?').
condicion(164, no_da_imagen, '¿Laptop enciende pero sin video?').
condicion(165, se_traba, '¿Puso memorias de distinta vel?').
condicion(166, no_enciende, '¿Recibió descarga eléctrica?').
condicion(167, se_traba, '¿Solo falla con cargador puesto?').
condicion(168, no_enciende, '¿Puso módulo de 16GB o 32GB?').
condicion(169, pantallazo_azul, '¿Módulo tiene chips por ambos lados?').
condicion(170, no_da_imagen, '¿RAM marca genérica sin logo?').
condicion(171, ventilador_ruidoso, '¿Sale poco aire por rejillas?').
condicion(172, ruido_extraño, '¿Vibra toda la laptop?').
condicion(173, se_apaga_solo, '¿Se apaga en menos de 5 min?').
condicion(174, ventilador_ruidoso, '¿Fan al 100% sin hacer nada?').
condicion(175, laptop_caliente, '¿Tiene más de 2 años de uso?').
condicion(176, se_apaga_solo, '¿La usa sobre la cama?').
condicion(177, laptop_lenta, '¿Solo es rápida conectada?').
condicion(178, ventilador_ruidoso, '¿CPU al 100% en reposo?').
condicion(179, laptop_caliente, '¿Usa funda protectora puesta?').
condicion(180, se_apaga_solo, '¿Marca 100C pero aire sale frío?').
condicion(181, imagen_distorsionada, '¿Aparecen manchas negras?').
condicion(182, sin_brillo, '¿Se ve imagen muy al fondo?').
condicion(183, imagen_distorsionada, '¿Rayas cambian al mover tapa?').
condicion(184, sin_brillo, '¿Pantalla prendió roja y murió?').
condicion(185, pantalla_negra, '¿Cree que está cerrada la tapa?').
condicion(186, imagen_distorsionada, '¿Pantalla se ve fuera de cuadro?').
condicion(187, pantallazo_azul, '¿Error VIDEO_TDR_FAILURE?').
condicion(188, parpadeo_pantalla, '¿Pantalla es de alta tasa Hz?').
condicion(189, imagen_distorsionada, '¿Tiene puntitos fijos brillantes?').
condicion(190, ruido_en_audio, '¿Bocinas zumban cerca de celular?').
condicion(191, ruido_en_audio, '¿Audio pita solo con cargador?').
condicion(192, ruido_en_audio, '¿Ruido desaparece al tocarla?').
condicion(193, audio_fallido, '¿Se rompió plug de audífonos?').
condicion(194, sin_audio, '¿Marca dispositivo no instalado?').
condicion(195, teclas_no_funcionan, '¿Siente las teclas pegajosas?').
condicion(196, mouse_no_mueve, '¿Luz de touchpad está naranja?').
condicion(197, sin_internet, '¿No detecta ninguna red?').
condicion(198, señal_wifi_debil, '¿Solo funciona pegado al modem?').
condicion(199, no_enciende, '¿Se apagó actualizando sistema?').
condicion(200, ruido_extraño, '¿Cruje al abrir la laptop?').


% --- hechos.pl: Información de Diagnóstico (201-300) tercer bloque de la matriz de hechos---

falla_info(201, 'PC', 'Puerto PS/2 dañado', 'Usar adaptador USB o cambiar placa.').
falla_info(202, 'PC', 'Interferencia en señal VGA', 'Usar cable con núcleos de ferrita.').
falla_info(203, 'PC', 'Puerto HDMI sin masa', 'Probar con otro monitor o puerto.').
falla_info(204, 'PC', 'Controlador USB saturado', 'Desconectar dispositivos no esenciales.').
falla_info(205, 'PC', 'Falla de tarjeta de red PCIe', 'Cambiar a puerto PCIe x1 inferior.').
falla_info(206, 'PC', 'Batería CMOS de 3.3V baja', 'Reemplazar por una CR2032 nueva.').
falla_info(207, 'PC', 'Sensor de temperatura falso', 'Ignorar en BIOS o actualizar Microcode.').
falla_info(208, 'PC', 'Chip de audio quemado', 'Instalar tarjeta de sonido dedicada.').
falla_info(209, 'PC', 'Error de suma de comprobación', 'Resetear valores por defecto en BIOS.').
falla_info(210, 'PC', 'Cortocircuito en panel frontal', 'Revisar cables de Power/Reset.').
falla_info(211, 'PC', 'Lector de discos trabado', 'Usar orificio de expulsión manual.').
falla_info(212, 'PC', 'Falla de sensor de ventilador', 'Conectar fan directo a Molex/SATA.').
falla_info(213, 'PC', 'Gabinete con estática acumulada', 'Verificar tierra física del contacto.').
falla_info(214, 'PC', 'Cables de datos enrollados', 'Acomodar cables lejos de energía.').
falla_info(215, 'PC', 'Puerto eSATA no habilitado', 'Activar modo Hot Plug en BIOS.').
falla_info(216, 'PC', 'Error de paridad DMA', 'Desactivar overclock de bus PCIe.').
falla_info(217, 'PC', 'Falla de chip Super I/O', 'Cambio de placa madre necesario.').
falla_info(218, 'PC', 'Conector de audio frontal roto', 'Usar puertos traseros de la placa.').
falla_info(219, 'PC', 'Incompatibilidad de teclado RGB', 'Actualizar firmware del teclado.').
falla_info(220, 'PC', 'Puerto serie/com desalineado', 'Revisar pines en el header de placa.').
falla_info(221, 'Laptop', 'Lector de huellas sucio', 'Limpiar con cinta adhesiva suave.').
falla_info(222, 'Laptop', 'Webcam bloqueada físicamente', 'Abrir pestaña de privacidad manual.').
falla_info(223, 'Laptop', 'Micrófono interno desconectado', 'Revisar conexión junto a la cámara.').
falla_info(224, 'Laptop', 'Bisagra endurecida', 'Lubricar o aflojar tuerca de bisagra.').
falla_info(225, 'Laptop', 'Pantalla con efecto ghosting', 'Bajar tasa de refresco a 60Hz.').
falla_info(226, 'Laptop', 'Touchpad con jitter', 'Usar cargador original (ruido AC).').
falla_info(227, 'Laptop', 'Batería hinchada (Spicy Pillow)', 'Retirar inmediatamente y reciclar.').
falla_info(228, 'Laptop', 'Teclado con ghosting', 'Desactivar filtros en accesibilidad.').
falla_info(229, 'Laptop', 'Slot SD con pines doblados', 'Enderezar o usar lector externo.').
falla_info(230, 'Laptop', 'Modo avión activado por hardware', 'Presionar combinación de teclas Fn.').
falla_info(231, 'Laptop', 'Falla de sensor Hall (Tapa)', 'Alejar imanes del equipo.').
falla_info(232, 'Laptop', 'Altavoces con membrana rota', 'Reemplazar parlantes internos.').
falla_info(233, 'Laptop', 'Puerto USB-C sin Power Delivery', 'Usar el puerto marcado con rayo/enchufe.').
falla_info(234, 'Laptop', 'Sobrecalentamiento de PCH', 'Aplicar pad térmico extra si es posible.').
falla_info(235, 'Laptop', 'Falla de retroiluminación teclado', 'Revisar cable flex pequeño de luz.').
falla_info(236, 'Laptop', 'Luz de encendido parpadea código', 'Buscar código de error en sitio oficial.').
falla_info(237, 'Laptop', 'Módulo TPM deshabilitado', 'Activar Security Chip en BIOS.').
falla_info(238, 'Laptop', 'Smart Card reader fallido', 'Actualizar driver de seguridad.').
falla_info(239, 'Laptop', 'Antena Wifi rota en bisagra', 'Reemplazar cable coaxial de antena.').
falla_info(240, 'Laptop', 'Puerto Kensington trabado', 'No forzar; usar lubricante seco.').
falla_info(241, 'PC', 'Interferencia de mouse inalámbrico', 'Usar extensor USB para el receptor.').
falla_info(242, 'PC', 'Falla de fuente en línea -12V', 'Probar con fuente certificada.').
falla_info(243, 'PC', 'BIOS bloqueada por password', 'Retirar pila y puentear CLR_CMOS.').
falla_info(244, 'PC', 'Error de CPU Fan Speed', 'Poner Ignore en monitoreo de BIOS.').
falla_info(245, 'PC', 'Monitor detectado como Genérico', 'Instalar archivo .INF del monitor.').
falla_info(246, 'PC', 'Inestabilidad por modo CSM', 'Cambiar a modo UEFI nativo.').
falla_info(247, 'PC', 'Puerto LAN con LED naranja fijo', 'Revisar si el cable es Cat5e o superior.').
falla_info(248, 'PC', 'Ruido eléctrico (Coil Whine)', 'Limitar FPS en juegos o cambiar fuente.').
falla_info(249, 'PC', 'Cables de fuente derretidos', 'No usar adaptadores Molex a SATA.').
falla_info(250, 'PC', 'Placa base arqueada', 'Aflojar tornillos del chasis centrales.').
falla_info(251, 'Laptop', 'Pantalla con líneas verticales', 'Falla de controlador T-CON (Cambiar LCD).').
falla_info(252, 'Laptop', 'Cargador emite olor a ozono', 'Reemplazar cargador inmediatamente.').
falla_info(253, 'Laptop', 'Teclado escribe caracteres locos', 'Desinstalar idioma de teclado extra.').
falla_info(254, 'Laptop', 'Touchpad se levanta solo', 'Batería interna inflándose abajo.').
falla_info(255, 'Laptop', 'Falla de BIOS tras hibernación', 'Desactivar Inicio Rápido en Windows.').
falla_info(256, 'Laptop', 'Bluetooth desaparece', 'Reinstalar driver de chipset primero.').
falla_info(257, 'Laptop', 'Brillo no se puede ajustar', 'Actualizar driver de video integrado.').
falla_info(258, 'Laptop', 'Laptop no suspende al cerrar', 'Revisar sensor de imán en marco.').
falla_info(259, 'Laptop', 'Puerto Thunderbolt no reconoce', 'Actualizar firmware de Thunderbolt.').
falla_info(260, 'Laptop', 'Audio suena robótico', 'Cambiar formato a 16-bit 44100Hz.').
falla_info(261, 'PC', 'Error de lectura USB 3.0', 'Instalar drivers XHCI específicos.').
falla_info(262, 'PC', 'Falla de puerto DisplayPort', 'Apagar monitor y desconectar 1 min.').
falla_info(263, 'PC', 'SSD NVMe no detectado', 'Habilitar modo M.2 PCIe en BIOS.').
falla_info(264, 'PC', 'Reinicios al conectar audio', 'Corto en jack frontal (No usarlo).').
falla_info(265, 'PC', 'Congelamiento por ahorro energía', 'Desactivar C-States en BIOS.').
falla_info(266, 'PC', 'Error de Secure Boot', 'Instalar llaves de fábrica en BIOS.').
falla_info(267, 'PC', 'Led de Debug CPU encendido', 'Revisar pines de alimentación EPS.').
falla_info(268, 'PC', 'Led de Debug DRAM encendido', 'Probar RAM en slots 2 y 4 solamente.').
falla_info(269, 'PC', 'Led de Debug VGA encendido', 'Resentar GPU o limpiar contactos.').
falla_info(270, 'PC', 'Led de Debug BOOT encendido', 'Conectar unidad con sistema operativo.').
falla_info(271, 'Laptop', 'HDD vibra mucho', 'Instalar gomas anti-vibración.').
falla_info(272, 'Laptop', 'SSD SATA no entra en slot', 'Revisar si es de 7mm o 9.5mm.').
falla_info(273, 'Laptop', 'Batería dice 0% disponible', 'Calibrar ciclo de carga/descarga.').
falla_info(274, 'Laptop', 'Carcasa de plástico rota', 'Usar pegamento epóxico para plástico.').
falla_info(275, 'Laptop', 'Wifi lento en 2.4GHz', 'Cambiar canal del router a 1, 6 o 11.').
falla_info(276, 'Laptop', 'Bluetooth tiene lag', 'Desactivar ahorro energía en Device Mgr.').
falla_info(277, 'Laptop', 'No reconoce cargador original', 'Limpiar pin central con alcohol.').
falla_info(278, 'Laptop', 'Pantalla parpadea en gris', 'Revisar conexión cable LVDS.').
falla_info(279, 'Laptop', 'Teclado no funciona en BIOS', 'Habilitar Legacy USB Support.').
falla_info(280, 'Laptop', 'Webcam se ve muy oscura', 'Aumentar exposición en ajustes app.').
falla_info(281, 'PC', 'Puerto USB da toques', 'Invertir posición de enchufe pared.').
falla_info(282, 'PC', 'Humo blanco en arranque', 'Falla de capacitor electrolítico.').
falla_info(283, 'PC', 'Olor a huevo podrido', 'Batería de UPS fallando (ácido).').
falla_info(284, 'PC', 'Pitidos constantes rápidos', 'Falla de controlador de teclado.').
falla_info(285, 'PC', 'Pantalla se apaga al jugar', 'Fuente no aguanta picos de GPU.').
falla_info(286, 'PC', 'Error de Fan de Chasis', 'Conectar fan en puerto SYS_FAN.').
falla_info(287, 'PC', 'Velocidad de internet baja', 'Desactivar Green Ethernet en driver.').
falla_info(288, 'PC', 'Periféricos no despiertan PC', 'Activar Wake on USB en BIOS.').
falla_info(289, 'PC', 'Falla de lectura SD frontal', 'Revisar cable interno USB 2.0.').
falla_info(290, 'PC', 'Ruido de estática en grabación', 'Bajar ganancia de micro a +10dB.').
falla_info(291, 'Laptop', 'Touchpad loco al cargar', 'Cargador genérico sin filtrado.').
falla_info(292, 'Laptop', 'Se calienta cerrada', 'Desactivar Modern Standby.').
falla_info(293, 'Laptop', 'Puerto HDMI flojo', 'Resoldar pines de soporte.').
falla_info(294, 'Laptop', 'Slot Kensington se rompió', 'Usar candado de seguridad USB.').
falla_info(295, 'Laptop', 'Wifi no ve redes 5GHz', 'Tarjeta wifi antigua (Solo 2.4).').
falla_info(296, 'Laptop', 'Audio solo por un lado', 'Revisar balance en panel sonido.').
falla_info(297, 'Laptop', 'Batería no carga al 100%', 'Desactivar Battery Health Manager.').
falla_info(298, 'Laptop', 'Teclado suena hueco', 'Ajustar tornillos de retención teclado.').
falla_info(299, 'Laptop', 'Pantalla con manchas blancas', 'Presión excesiva sobre panel LCD.').
falla_info(300, 'Laptop', 'No reconoce SSD NVMe Gen4', 'Slot solo soporta Gen3 (Incompatible).').

% --- hechos.pl: Lógica de Preguntas (201-300) ---

condicion(201, periferico_no_detectado, '¿Usa teclado de pin redondo morado?').
condicion(202, imagen_distorsionada, '¿Ve sombras en las letras (ghosting)?').
condicion(203, sin_imagen, '¿Pantalla marca No Signal en HDMI?').
condicion(204, periferico_no_detectado, '¿Conecta más de 5 USBs traseros?').
condicion(205, sin_internet, '¿Tarjeta de red es una placa extra?').
condicion(206, no_guarda_hora, '¿Aparece CMOS Battery Low al prender?').
condicion(207, ventilador_ruidoso, '¿Marca 120 grados apenas enciende?').
condicion(208, sin_audio, '¿No detecta bocinas ni audífonos?').
condicion(209, no_bootea, '¿Dice CMOS Checksum Error?').
condicion(210, no_enciende, '¿Enciende al quitar cables de Reset?').
condicion(211, ruido_extraño, '¿Lector de CD hace ruido de traba?').
condicion(212, ventilador_ruidoso, '¿Fan gira pero BIOS marca 0 RPM?').
condicion(213, periferico_no_detectado, '¿Mouse falla solo en días secos?').
condicion(214, se_traba, '¿Cables SATA están muy doblados?').
condicion(215, disco_no_detectado, '¿Usa puerto eSATA externo?').
condicion(216, pantallazo_azul, '¿Error dice WHEA o DMA_ERROR?').
condicion(217, no_enciende, '¿No funcionan ni USBs ni teclado?').
condicion(218, audio_fallido, '¿Audio se corta al mover el plug?').
condicion(219, periferico_no_detectado, '¿Teclado prende pero no escribe?').
condicion(220, periferico_no_detectado, '¿Puerto serial no comunica datos?').
condicion(221, no_inicia_sesion, '¿Huella falla tras comer/sudar?').
condicion(222, pantalla_negra, '¿Webcam no abre pero led prende?').
condicion(223, sin_audio, '¿No lo escuchan en llamadas?').
condicion(224, ruido_extraño, '¿Truena al abrir la pantalla?').
condicion(225, imagen_distorsionada, '¿Ve estelas al mover ventanas?').
condicion(226, mouse_no_mueve, '¿Touchpad salta solo con cargador?').
condicion(227, mouse_no_mueve, '¿Touchpad se siente duro o salido?').
condicion(228, teclas_no_funcionan, '¿Presiona una tecla y salen dos?').
condicion(229, disco_no_detectado, '¿No lee tarjetas SD laterales?').
condicion(230, sin_internet, '¿Icono de avión está fijo?').
condicion(231, pantalla_negra, '¿Se apaga al acercar un celular?').
condicion(232, audio_distorsionado, '¿Bocinas suenan como cartón roto?').
condicion(233, no_carga, '¿Carga por USB-C pero es muy lento?').
condicion(234, se_traba, '¿Centro de laptop quema por abajo?').
condicion(235, teclas_no_funcionan, '¿Teclas no brillan en la noche?').
condicion(236, no_enciende, '¿Led de carga parpadea 3+2 veces?').
condicion(237, no_bootea, '¿Windows 11 dice PC no compatible?').
condicion(238, periferico_no_detectado, '¿No lee tarjetas de banco/ID?').
condicion(239, señal_wifi_debil, '¿Wifi falla al mover la pantalla?').
condicion(240, ruido_extraño, '¿Candado de seguridad no abre?').
condicion(241, mouse_no_mueve, '¿Mouse inalámbrico se traba?').
condicion(242, reinicia_solo, '¿Tiene placa de sonido de gama alta?').
condicion(243, no_bootea, '¿Pide password apenas prende?').
condicion(244, no_enciende, '¿Error CPU Fan Not Detected?').
condicion(245, imagen_distorsionada, '¿No puede subir la resolución?').
condicion(246, no_bootea, '¿Instaló Windows en modo antiguo?').
condicion(247, sin_internet, '¿Luz de red atrás no parpadea?').
condicion(248, ruido_extraño, '¿Escucha un silbido al jugar?').
condicion(249, no_enciende, '¿Cables huelen a plástico quemado?').
condicion(250, no_da_imagen, '¿Placa se ve curva en el gabinete?').
condicion(251, imagen_distorsionada, '¿Ve una raya fija de color?').
condicion(252, no_enciende, '¿Cargador hace ruido o huele mal?').
condicion(253, teclas_no_funcionan, '¿La Ñ escribe otro símbolo?').
condicion(254, mouse_no_mueve, '¿Se siente un bulto bajo touchpad?').
condicion(255, no_enciende, '¿No prende tras dejarla hibernar?').
condicion(256, sin_internet, '¿No aparece el icono de Bluetooth?').
condicion(257, imagen_distorsionada, '¿Brillo está siempre al 100%?').
condicion(258, bateria_dura_poco, '¿Batería se agota estando cerrada?').
condicion(259, periferico_no_detectado, '¿Puerto USB-C no da video/datos?').
condicion(260, audio_distorsionado, '¿Audio suena como un robot?').
condicion(261, disco_lento, '¿USB 3.0 transfiere como 2.0?').
condicion(262, sin_imagen, '¿DP no da imagen tras suspensión?').
condicion(263, disco_no_detectado, '¿No ve el SSD M.2 en la BIOS?').
condicion(264, reinicia_solo, '¿Se reinicia al poner audífonos?').
condicion(265, se_traba, '¿Se congela al no usarla nada?').
condicion(266, no_bootea, '¿Error Secure Boot Violation?').
condicion(267, no_enciende, '¿Led rojo fijo dice CPU?').
condicion(268, no_da_imagen, '¿Led rojo fijo dice DRAM?').
condicion(269, no_da_imagen, '¿Led rojo fijo dice VGA?').
condicion(270, no_bootea, '¿Led rojo fijo dice BOOT?').
condicion(271, ruido_extraño, '¿Laptop zumba al leer datos?').
condicion(272, disco_no_detectado, '¿Tapa de laptop no cierra bien?').
condicion(273, bateria_dura_poco, '¿Se apaga al 30% de golpe?').
condicion(274, ruido_extraño, '¿Pedazos de plástico caen dentro?').
condicion(275, sin_internet, '¿Internet va y viene en laptop?').
condicion(276, mouse_no_mueve, '¿Mouse BT se duerme cada 5 seg?').
condicion(277, no_carga, '¿Dice Conectado pero no carga?').
condicion(278, imagen_distorsionada, '¿Pantalla se pone gris a ratos?').
condicion(279, teclas_no_funcionan, '¿Teclado no sirve para entrar BIOS?').
condicion(280, imagen_distorsionada, '¿Imagen de cámara tiene mucho ruido?').
condicion(281, no_enciende, '¿Le dio un toque fuerte al tocar USB?').
condicion(282, no_enciende, '¿Salió humo blanco de la placa?').
condicion(283, ruido_extraño, '¿Huele mal cerca de la PC?').
condicion(284, no_enciende, '¿Pita mucho antes de dar imagen?').
condicion(285, se_apaga_solo, '¿Se apaga solo al jugar mucho?').
condicion(286, ventilador_ruidoso, '¿Fan de chasis va muy rápido?').
condicion(287, sin_internet, '¿Internet no pasa de 100 Mbps?').
condicion(288, se_traba, '¿No despierta de modo reposo?').
condicion(289, periferico_no_detectado, '¿No lee memorias de cámaras SD?').
condicion(290, audio_distorsionado, '¿Micrófono tiene mucho siseo?').
condicion(291, mouse_no_mueve, '¿Touchpad falla sin cargador?').
condicion(292, laptop_caliente, '¿Se calienta dentro de la mochila?').
condicion(293, sin_imagen, '¿Mueve el cable HDMI y se corta?').
condicion(294, ruido_extraño, '¿Intentaron robar la laptop?').
condicion(295, sin_internet, '¿No ve la red Wifi de su casa?').
condicion(296, sin_audio, '¿Solo se oye una bocina interna?').
condicion(297, bateria_dura_poco, '¿Batería se queda en 80%?').
condicion(298, ruido_extraño, '¿Teclado vibra al escribir?').
condicion(299, imagen_distorsionada, '¿Ve puntos blancos en fondo negro?').
condicion(300, disco_no_detectado, '¿SSD M.2 es de última generación?').


% --- hechos.pl: Información de Diagnóstico (301-400) cuarto bloque de matriz de hechos ---

falla_info(301, 'PC', 'Conflicto de IRQ Legacy', 'Cambiar tarjeta a otro slot PCIe.').
falla_info(302, 'PC', 'Controlador USB 3.1 sin driver', 'Descargar driver de chipset oficial.').
falla_info(303, 'PC', 'Falla de Handshake HDMI', 'Encender monitor antes que la PC.').
falla_info(304, 'PC', 'Sobrecarga en puerto PS/2', 'Apagar PC antes de conectar periférico.').
falla_info(305, 'PC', 'Error de paridad en puente sur', 'Bajar frecuencia del bus en BIOS.').
falla_info(306, 'PC', 'Pila CMOS con falso contacto', 'Limpiar soporte de la pila con alcohol.').
falla_info(307, 'PC', 'Ventilador con rodamiento seco', 'Reemplazar ventilador de chasis.').
falla_info(308, 'PC', 'Capa de polvo conductor', 'Limpieza profunda con brocha antiestática.').
falla_info(309, 'PC', 'Falla de puerto Serial/COM', 'Verificar voltaje en pines con multímetro.').
falla_info(310, 'PC', 'Lector de tarjetas interno sucio', 'Usar aire comprimido en la ranura.').
falla_info(311, 'PC', 'SSD NVMe Gen4 en slot Gen3', 'Mover a slot principal (cerca al CPU).').
falla_info(312, 'PC', 'Error de bit de parada en RAM', 'Aumentar latencia CAS en 1 punto.').
falla_info(313, 'PC', 'Falla de fase de poder (VRM)', 'Cambiar placa (daño permanente).').
falla_info(314, 'PC', 'Capacitor sólido inflado', 'Soldar capacitor nuevo del mismo valor.').
falla_info(315, 'PC', 'Oxidación en contactos PCIe', 'Limpiar con goma de borrar azul.').
falla_info(316, 'PC', 'Configuración de RAID rota', 'Reconstruir arreglo desde controladora.').
falla_info(317, 'PC', 'Falla de chip de Red Realtek', 'Desactivar en BIOS y usar USB-LAN.').
falla_info(318, 'PC', 'Ruido por bucle de tierra', 'Conectar monitor y PC al mismo regulador.').
falla_info(319, 'PC', 'Incompatibilidad de ratón RGB', 'Cambiar puerto USB 2.0 a 3.0.').
falla_info(320, 'PC', 'Falla de sensor de intrusión', 'Poner jumper en conector JCI1.').
falla_info(321, 'Laptop', 'Lector de huellas descalibrado', 'Borrar y volver a registrar huella.').
falla_info(322, 'Laptop', 'Webcam sin permiso de Windows', 'Habilitar acceso en Privacidad.').
falla_info(323, 'Laptop', 'Micrófono con ganancia baja', 'Subir nivel en Panel de Sonido.').
falla_info(324, 'Laptop', 'Bisagra suelta (Tornillos)', 'Apretar tornillos internos de base.').
falla_info(325, 'Laptop', 'Pantalla con fugas de luz', 'Aflojar un poco el marco plástico.').
falla_info(326, 'Laptop', 'Touchpad con sensibilidad alta', 'Ajustar en Configuración de gestos.').
falla_info(327, 'Laptop', 'Batería con celdas desbalanceadas', 'Hacer ciclo de carga de 12 horas.').
falla_info(328, 'Laptop', 'Teclado con delay (Retraso)', 'Desactivar Teclas de Filtro.').
falla_info(329, 'Laptop', 'Lector SD detecta pero no lee', 'Desbloquear pestaña física de la SD.').
falla_info(330, 'Laptop', 'Wifi bloqueado por software', 'Activar con tecla Fn + F12 (o similar).').
falla_info(331, 'Laptop', 'Sensor de proximidad sucio', 'Limpiar marco superior de la pantalla.').
falla_info(332, 'Laptop', 'Bocinas con limalla metálica', 'Limpiar rejillas con imán pequeño.').
falla_info(333, 'Laptop', 'Puerto USB-C con polvo', 'Limpiar con cepillo fino e isopropílico.').
falla_info(334, 'Laptop', 'Sobrecalentamiento de SSD M.2', 'Instalar disipador ultra-delgado.').
falla_info(335, 'Laptop', 'Luz de teclado no enciende', 'Revisar sensor de luz ambiental.').
falla_info(336, 'Laptop', 'Error de suma de BIOS', 'Refrescar BIOS con archivo .cap.').
falla_info(337, 'Laptop', 'Chip TPM 2.0 oculto', 'Habilitar Intel PTT o AMD fTPM.').
falla_info(338, 'Laptop', 'Smart Card con driver viejo', 'Descargar driver de Microsoft Update.').
falla_info(339, 'Laptop', 'Wifi con cable coaxial pelado', 'Aislar con cinta capton.').
falla_info(340, 'Laptop', 'Chasis de aluminio deformado', 'Enderezar con presión leve (sin placa).').
falla_info(341, 'PC', 'Interferencia de WiFi en Mouse', 'Cambiar canal de WiFi de 2.4 a 5GHz.').
falla_info(342, 'PC', 'Falla de voltaje en riel 5V', 'Probar fuente con voltímetro.').
falla_info(343, 'PC', 'BIOS bloqueada por Admin', 'Cortocircuitar pines de Password.').
falla_info(344, 'PC', 'Falla de lectura de RPM', 'Cambiar ventilador de 3 a 4 pines.').
falla_info(345, 'PC', 'Monitor con perfil de color mal', 'Cargar perfil sRGB estándar.').
falla_info(346, 'PC', 'Arranque UEFI muy lento', 'Desactivar arranque por red (PXE).').
falla_info(347, 'PC', 'Puerto LAN sin IP válida', 'Reiniciar pila TCP/IP con netsh.').
falla_info(348, 'PC', 'Vibración de discos mecánicos', 'Usar arandelas de goma en tornillos.').
falla_info(349, 'PC', 'Cables de panel frontal al revés', 'Verificar polaridad (+/-) de LEDs.').
falla_info(350, 'PC', 'Placa base con flexión térmica', 'Instalar backplate de CPU reforzado.').
falla_info(351, 'Laptop', 'Líneas horizontales en LCD', 'Falla de pegado de flex COF.').
falla_info(352, 'Laptop', 'Cargador con cable trozado', 'Soldar o comprar cargador nuevo.').
falla_info(353, 'Laptop', 'Teclado escribe solo', 'Limpiar debajo de la tecla pegada.').
falla_info(354, 'Laptop', 'Touchpad no detecta clics', 'Ajustar tornillo de presión central.').
falla_info(355, 'Laptop', 'Falla tras suspensión', 'Actualizar Management Engine (IME).').
falla_info(356, 'Laptop', 'Bluetooth con interferencia', 'Alejar dispositivos USB 3.0.').
falla_info(357, 'Laptop', 'Brillo se baja solo', 'Desactivar Brillo Adaptativo.').
falla_info(358, 'Laptop', 'No reconoce batería nueva', 'Hacer reset de controlador EC.').
falla_info(359, 'Laptop', 'Puerto Thunderbolt bloqueado', 'Habilitar seguridad en BIOS.').
falla_info(360, 'Laptop', 'Sonido con chasquidos', 'Desactivar mejoras de audio en Windows.').
falla_info(361, 'PC', 'USB reconoce como 1.1', 'Limpiar puerto con limpia-contactos.').
falla_info(362, 'PC', 'Falla de DisplayPort (Deep Sleep)', 'Desactivar DP 1.2/1.4 en monitor.').
falla_info(363, 'PC', 'SSD NVMe invisible en instalador', 'Cargar driver VMD de Intel.').
falla_info(364, 'PC', 'Reinicios por corto en USB', 'Revisar que no haya pines doblados.').
falla_info(365, 'PC', 'Congelamiento por C-States', 'Cambiar Power Supply Idle Control.').
falla_info(366, 'PC', 'Secure Boot impide boot USB', 'Poner en modo Custom en BIOS.').
falla_info(367, 'PC', 'Falla de CPU (Voltaje)', 'Subir 0.05v al VCore (Estabilizar).').
falla_info(368, 'PC', 'RAM en slots incorrectos', 'Mover a slots A2 y B2 (2 y 4).').
falla_info(369, 'PC', 'GPU mal asentada', 'Quitar y poner con fuerza uniforme.').
falla_info(370, 'PC', 'Error de arranque (BCD)', 'Ejecutar bootrec /rebuildbcd.').
falla_info(371, 'Laptop', 'HDD con ruido de rascado', 'Falla de cabezales (Cambiar ya).').
falla_info(372, 'Laptop', 'SSD M.2 se sale del slot', 'Instalar tornillo de fijación M2.').
falla_info(373, 'Laptop', 'Batería se descarga apagada', 'Desactivar Always-on USB en BIOS.').
falla_info(374, 'Laptop', 'Carcasa cruje al moverla', 'Poner cinta doble cara en uniones.').
falla_info(375, 'Laptop', 'WiFi no conecta a redes ocultas', 'Configurar conexión manual en panel.').
falla_info(376, 'Laptop', 'Mouse Bluetooth se desconecta', 'Cambiar plan de energía de tarjeta.').
falla_info(377, 'Laptop', 'Cargador calienta demasiado', 'Usar cargador de mayor vataje.').
falla_info(378, 'Laptop', 'Pantalla parpadea al conectar', 'Revisar frecuencia de refresco.').
falla_info(379, 'Laptop', 'Teclado no detecta Fn', 'Instalar Driver de Hotkeys de marca.').
falla_info(380, 'Laptop', 'Webcam con imagen morada', 'Falla de sensor IR (Cambio cámara).').
falla_info(381, 'PC', 'Electricidad estática en audio', 'Usar aislador de bucle de tierra.').
falla_info(382, 'PC', 'Chispas en fuente de poder', 'Falla crítica de varistor.').
falla_info(383, 'PC', 'Olor a quemado (Plástico)', 'Revisar conectores Molex-SATA.').
falla_info(384, 'PC', 'Pitidos 1 largo 2 cortos', 'Falla de memoria de video (GPU).').
falla_info(385, 'PC', 'Se apaga al conectar HDMI', 'Cortocircuito en puerto de video.').
falla_info(386, 'PC', 'Fan de CPU gira al máximo', 'Activar control PWM en BIOS.').
falla_info(387, 'PC', 'Internet pierde paquetes', 'Reemplazar conectores RJ45.').
falla_info(388, 'PC', 'No entra a BIOS con USB', 'Usar puerto USB 2.0 (Negro).').
falla_info(389, 'PC', 'Lector SD marca protegido', 'Bajar switch físico en tarjeta.').
falla_info(390, 'PC', 'Audio suena muy bajo', 'Revisar impedancia en driver.').
falla_info(391, 'Laptop', 'Touchpad se traba al azar', 'Actualizar driver de I2C HID.').
falla_info(392, 'Laptop', 'Se calienta en reposo', 'Revisar Windows Update pendiente.').
falla_info(393, 'Laptop', 'Puerto HDMI tiene juego', 'Reforzar con soldadura fría.').
falla_info(394, 'Laptop', 'Bloqueo de seguridad Kensington', 'Registrar llave en sitio oficial.').
falla_info(395, 'Laptop', 'WiFi no detecta canal 13', 'Cambiar región de tarjeta a Global.').
falla_info(396, 'Laptop', 'Solo funciona un audífono', 'Limpiar Jack con hisopo seco.').
falla_info(397, 'Laptop', 'Batería cargada al 60%', 'Desactivar modo Conservación.').
falla_info(398, 'Laptop', 'Teclado se siente flojo', 'Apretar tornillos traseros de chasis.').
falla_info(399, 'Laptop', 'Puntos brillantes en LCD', 'Presión de tornillos de tapa.').
falla_info(400, 'Laptop', 'Incompatibilidad con SSD DRAMless', 'Usar SSD con memoria caché.').


% --- hechos.pl: Lógica de Preguntas (301-400) ---

condicion(301, periferico_falla, '¿Es una tarjeta de red muy antigua?').
condicion(302, usb_no_reconoce, '¿Aparece dispositivo desconocido en USB?').
condicion(303, sin_imagen, '¿Pantalla enciende pero se queda negra?').
condicion(304, teclado_no_funciona, '¿Conecta el teclado con la PC prendida?').
condicion(305, pantallazo_azul, '¿Error dice BUS_CONTROL_ERROR?').
condicion(306, no_guarda_hora, '¿La pila es nueva pero no guarda hora?').
condicion(307, ruido_extraño, '¿Suena como un motor viejo?').
condicion(308, reinicia_solo, '¿Hay mucha pelusa dentro de la PC?').
condicion(309, periferico_falla, '¿Usa básculas o impresoras viejas?').
condicion(310, periferico_falla, '¿No lee ninguna memoria SD interna?').
condicion(311, disco_lento, '¿SSD Gen4 rinde a la mitad?').
condicion(312, pantallazo_azul, '¿Error dice PAGE_FAULT_IN_NONPAGED?').
condicion(313, no_enciende, '¿Vio una chispa cerca del procesador?').
condicion(314, reinicia_solo, '¿Se ven botes hinchados en la placa?').
condicion(315, no_da_imagen, '¿Tarjeta de video tiene contactos negros?').
condicion(316, disco_no_detectado, '¿Dice RAID Status: Degraded?').
condicion(317, sin_internet, '¿Desapareció el icono de red cableada?').
condicion(318, ruido_en_audio, '¿Escucha un zumbido constante?').
condicion(319, mouse_se_traba, '¿Luces del ratón parpadean y se apaga?').
condicion(320, no_bootea, '¿Dice Chassis Intrusion detected?').
condicion(321, no_inicia_sesion, '¿Lector de huellas no responde?').
condicion(322, webcam_no_abre, '¿Cámara se ve negra pero led prende?').
condicion(323, sin_audio, '¿Le dicen que se escucha muy bajito?').
condicion(324, ruido_extraño, '¿La pantalla baila al escribir?').
condicion(325, imagen_distorsionada, '¿Ve luz blanca en las esquinas?').
condicion(326, mouse_no_mueve, '¿Puntero salta por toda la pantalla?').
condicion(327, bateria_dura_poco, '¿Batería baja de 80% a 20% en minutos?').
condicion(328, teclado_falla, '¿Siente que escribe y tarda en salir?').
condicion(329, usb_no_reconoce, '¿Tarjeta SD marca Protegido?').
condicion(330, sin_internet, '¿Wifi marcado con una X roja?').
condicion(331, pantalla_negra, '¿Pantalla no prende al abrirla?').
condicion(332, audio_distorsionado, '¿Bocinas suenan metálicas?').
condicion(333, no_carga, '¿Cargador USB-C no entra bien?').
condicion(334, se_traba, '¿Siente caliente bajo la mano izquierda?').
condicion(335, teclado_falla, '¿Luces de teclas no prenden?').
condicion(336, no_enciende, '¿Led de encendido prende pero nada más?').
condicion(337, no_bootea, '¿No puede instalar Windows 11?').
condicion(338, periferico_falla, '¿Usa tarjetas inteligentes de acceso?').
condicion(339, sin_internet, '¿Wifi se corta al mover la tapa?').
condicion(340, ruido_extraño, '¿Carcasa se ve doblada o abierta?').
condicion(341, mouse_se_traba, '¿Mouse inalámbrico falla cerca de router?').
condicion(342, se_apaga_solo, '¿PC se apaga al conectar un disco duro?').
condicion(343, no_entra_bios, '¿BIOS le pide una clave que no sabe?').
condicion(344, ventilador_ruidoso, '¿Fan suena como turbina siempre?').
condicion(345, imagen_distorsionada, '¿Colores se ven muy amarillos/azules?').
condicion(346, no_bootea, '¿Tarda 1 minuto en mostrar el logo?').
condicion(347, sin_internet, '¿Dice Ethernet no tiene IP válida?').
condicion(348, ruido_extraño, '¿Gabinete vibra rítmicamente?').
condicion(349, no_enciende, '¿Acaba de armar la PC y no prende nada?').
condicion(350, se_traba, '¿Solo falla cuando hace mucho calor?').
condicion(351, imagen_distorsionada, '¿Ve líneas de colores horizontales?').
condicion(352, no_carga, '¿Carga solo si dobla el cable?').
condicion(353, teclado_falla, '¿Se escriben letras solas?').
condicion(354, mouse_no_mueve, '¿Touchpad no hace clic físico?').
condicion(355, no_enciende, '¿No despierta después de suspender?').
condicion(356, bluetooth_falla, '¿Audífonos BT se cortan mucho?').
condicion(357, imagen_distorsionada, '¿Pantalla cambia brillo sola?').
condicion(358, no_carga, '¿Batería dice 0% y no sube?').
condicion(359, usb_no_reconoce, '¿Puerto Thunderbolt no reconoce nada?').
condicion(360, audio_distorsionado, '¿Escucha clics en el audio?').
condicion(361, usb_no_reconoce, '¿USB dice dispositivo puede ir más rápido?').
condicion(362, sin_imagen, '¿Monitor no despierta con la PC?').
condicion(363, disco_no_detectado, '¿No aparece disco al instalar Windows?').
condicion(364, reinicia_solo, '¿Se reinicia al meter una memoria?').
condicion(365, se_traba, '¿Se congela al dejarla sin usar?').
condicion(366, no_bootea, '¿Error de firma digital al bootear?').
condicion(367, pantallazo_azul, '¿Error dice CLOCK_WATCHDOG_TIMEOUT?').
condicion(368, pantallazo_azul, '¿Puso 2 memorias en slots juntos?').
condicion(369, no_da_imagen, '¿VGA Led de la placa está prendido?').
condicion(370, no_bootea, '¿Dice Recovery: Windows no cargó bien?').
condicion(371, ruido_extraño, '¿Disco duro suena como rascado?').
condicion(372, disco_no_detectado, '¿Disco M.2 se ve flojo?').
condicion(373, bateria_dura_poco, '¿Pierde 10% de carga cada noche apagada?').
condicion(374, ruido_extraño, '¿Cruje al agarrarla de una esquina?').
condicion(375, sin_internet, '¿No encuentra redes Wifi ocultas?').
condicion(376, mouse_se_traba, '¿Mouse inalámbrico se duerme?').
condicion(377, no_carga, '¿Cargador quema al tocarlo?').
condicion(378, imagen_distorsionada, '¿Pantalla parpadea al conectar corriente?').
condicion(379, teclado_falla, '¿Botones de brillo/volumen no sirven?').
condicion(380, imagen_distorsionada, '¿Cámara se ve con colores raros?').
condicion(381, ruido_en_audio, '¿Oye estática al mover el mouse?').
condicion(382, no_enciende, '¿Vio chispas dentro de la fuente?').
condicion(383, no_enciende, '¿Huele a cable quemado dentro?').
condicion(384, no_da_imagen, '¿La PC pita 1 largo y 2 cortos?').
condicion(385, se_apaga_solo, '¿Se apaga al conectar la TV?').
condicion(386, ventilador_ruidoso, '¿Fan suena al máximo siempre?').
condicion(387, sin_internet, '¿Internet lento o se desconecta?').
condicion(388, no_entra_bios, '¿No puede entrar a la BIOS con teclado?').
condicion(389, usb_no_reconoce, '¿SD dice Solo Lectura?').
condicion(390, sin_audio, '¿Volumen está al 100% pero suena pasito?').
condicion(391, mouse_no_mueve, '¿Touchpad se congela a ratos?').
condicion(392, laptop_caliente, '¿Está muy caliente aunque no la use?').
condicion(393, hdmi_falla, '¿Imagen se va si mueve el cable?').
condicion(394, ruido_extraño, '¿Candado Kensington se trabó?').
condicion(395, sin_internet, '¿Laptop no ve redes Wifi 5G?').
condicion(396, sin_audio, '¿Audio solo se oye de un lado?').
condicion(397, no_carga, '¿Carga se detiene al 60% o 80%?').
condicion(398, teclado_falla, '¿Teclado se siente suelto al tacto?').
condicion(399, imagen_distorsionada, '¿Ve manchas brillantes en la pantalla?').
condicion(400, disco_lento, '¿SSD nuevo se traba mucho?').



% --- hechos.pl: Información de Diagnóstico (401-500) ultimo bnloque de la matriz de hechos ---

falla_info(401, 'PC', 'Conflicto de driver SMBus', 'Instalar driver de chipset AMD/Intel.').
falla_info(402, 'PC', 'Puerto USB 3.0 con ruido', 'Alejar receptores inalámbricos del puerto.').
falla_info(403, 'PC', 'Falla de cable HDMI direccional', 'Invertir el sentido del cable HDMI.').
falla_info(404, 'PC', 'Sobrevoltaje en puerto PS/2', 'Usar periféricos USB exclusivamente.').
falla_info(405, 'PC', 'Error de paridad de caché L3', 'Bajar frecuencia o voltaje de CPU.').
falla_info(406, 'PC', 'Sulfatación en base de pila', 'Limpiar con vinagre y luego alcohol.').
falla_info(407, 'PC', 'Ventilador con aspa rota', 'Reemplazar ventilador para evitar vibración.').
falla_info(408, 'PC', 'Corto por humedad ambiente', 'Usar deshumidificador en la habitación.').
falla_info(409, 'PC', 'Puerto COM con baudaje erróneo', 'Sincronizar velocidad en Administrador Disp.').
falla_info(410, 'PC', 'Lector de tarjetas con pin doblado', 'No usar; puede causar corto en USB.').
falla_info(411, 'PC', 'SSD NVMe Gen4 sin disipador', 'Instalar disipador pasivo de aluminio.').
falla_info(412, 'PC', 'Falla de refresco de DRAM', 'Aumentar parámetro tREFI en BIOS.').
falla_info(413, 'PC', 'Fase de poder (Choke) silbando', 'Aplicar barniz dieléctrico o cambiar placa.').
falla_info(414, 'PC', 'Capacitor cerámico en corto', 'Identificar con cámara térmica y retirar.').
falla_info(415, 'PC', 'Oxidación por ambiente salino', 'Usar gabinete con filtros de aire finos.').
falla_info(416, 'PC', 'Arreglo RAID 0 desincronizado', 'Recuperar datos y cambiar a RAID 1.').
falla_info(417, 'PC', 'Falla de chip LAN por rayo', 'Instalar tarjeta de red PCIe nueva.').
falla_info(418, 'PC', 'Bucle de tierra en GPU', 'Usar cable de video con mejor blindaje.').
falla_info(419, 'PC', 'Firmware de mouse corrupto', 'Reinstalar firmware desde web fabricante.').
falla_info(420, 'PC', 'Jumper de CMOS mal puesto', 'Colocar en posición 1-2 (Normal).').
falla_info(421, 'Laptop', 'Lector de huellas rayado', 'Pulir suavemente o reemplazar sensor.').
falla_info(422, 'Laptop', 'Webcam bloqueada por antivirus', 'Revisar permisos de protección de cámara.').
falla_info(423, 'Laptop', 'Micrófono con eco excesivo', 'Activar Cancelación de Eco en driver.').
falla_info(424, 'Laptop', 'Bisagra arrancada de chasis', 'Reparar anclajes con resina industrial.').
falla_info(425, 'Laptop', 'Pantalla con PWM parpadeante', 'Mantener brillo por encima del 50%.').
falla_info(426, 'Laptop', 'Touchpad con estática', 'Tocar parte metálica para descargar.').
falla_info(427, 'Laptop', 'Batería inflada presiona celdas', 'Reemplazar antes de que dañe el trackpad.').
falla_info(428, 'Laptop', 'Teclado con matriz cruzada', 'Cambiar teclado (daño por humedad).').
falla_info(429, 'Laptop', 'Slot SD con suciedad líquida', 'Limpiar con isopropílico y cepillo.').
falla_info(430, 'Laptop', 'Wifi apagado por BIOS', 'Habilitar Wireless Device en Security.').
falla_info(431, 'Laptop', 'Sensor Hall pegado (Imán)', 'Pasar imán suave para despegar sensor.').
falla_info(432, 'Laptop', 'Altavoces saturados de polvo', 'Limpiar con aire comprimido suave.').
falla_info(433, 'Laptop', 'Puerto USB-C sin datos', 'Probar con cable USB-C 3.1 (no de carga).').
falla_info(434, 'Laptop', 'M.2 NVMe sobre 80 grados', 'Mejorar ventilación de la base.').
falla_info(435, 'Laptop', 'Luz de teclado en corto', 'Desconectar cable flex de iluminación.').
falla_info(436, 'Laptop', 'Error de Checksum de BIOS', 'Cambiar pila CMOS interna (si tiene).').
falla_info(437, 'Laptop', 'Chip TPM no detectado', 'Habilitar en menú de Seguridad (PTT).').
falla_info(438, 'Laptop', 'Smart Card bloqueada', 'Contactar a soporte de IT corporativo.').
falla_info(439, 'Laptop', 'Antena Wifi cortada', 'Soldar filamento o cambiar antena.').
falla_info(440, 'Laptop', 'Chasis de magnesio fisurado', 'Cambiar carcasa superior (Palmrest).').
falla_info(441, 'PC', 'Mouse inalámbrico sin batería', 'Cargar o cambiar pilas del periférico.').
falla_info(442, 'PC', 'Falla de línea +3.3V', 'Reemplazar fuente de poder.').
falla_info(443, 'PC', 'BIOS protegida por empresa', 'Solicitar desbloqueo de departamento IT.').
falla_info(444, 'PC', 'CPU Fan con cable roto', 'Reparar soldadura de cables de fan.').
falla_info(445, 'PC', 'Monitor con tinte verdoso', 'Ajustar pines del cable VGA/DVI.').
falla_info(446, 'PC', 'Arranque UEFI corrupto', 'Reinstalar Windows en modo GPT.').
falla_info(447, 'PC', 'LAN con velocidad limitada', 'Verificar que el cable sea de 8 hilos.').
falla_info(448, 'PC', 'Ruido de HDD por desgaste', 'Respaldar datos inmediatamente.').
falla_info(449, 'PC', 'Leds frontales fundidos', 'Reemplazar Leds de 3mm en gabinete.').
falla_info(450, 'PC', 'Placa base con corto en base', 'Aislar con arandelas de cartón.').
falla_info(451, 'Laptop', 'LCD con manchas de presión', 'Evitar llevar laptop en mochila apretada.').
falla_info(452, 'Laptop', 'Cargador con plug flojo', 'Reemplazar punta del cargador.').
falla_info(453, 'Laptop', 'Teclado con teclas duras', 'Limpiar con aire y alcohol debajo.').
falla_info(454, 'Laptop', 'Touchpad no hace clic der.', 'Habilitar clic de dos dedos en driver.').
falla_info(455, 'Laptop', 'Falla tras hibernación prolongada', 'Borrar archivo hiberfil.sys y reiniciar.').
falla_info(456, 'Laptop', 'Bluetooth con señal pobre', 'Revisar conexión de antena en tarjeta.').
falla_info(457, 'Laptop', 'Brillo no cambia en batería', 'Ajustar plan de energía de video.').
falla_info(458, 'Laptop', 'Batería genérica rechazada', 'Usar batería con chip de marca.').
falla_info(459, 'Laptop', 'Thunderbolt en modo seguro', 'Cambiar Security Level en BIOS.').
falla_info(460, 'Laptop', 'Sonido con estática', 'Desinstalar driver de audio de terceros.').
falla_info(461, 'PC', 'USB 3.0 con interferencia EMI', 'Usar puertos USB 2.0 para dongles.').
falla_info(462, 'PC', 'DP sin señal tras mover PC', 'Asegurar que el cable haga clic.').
falla_info(463, 'PC', 'SSD M.2 en slot equivocado', 'Consultar manual para slot compartido.').
falla_info(464, 'PC', 'Reinicios por botón pegado', 'Limpiar botón de encendido con WD-40.').
falla_info(465, 'PC', 'Congelamiento por disco externo', 'Cambiar cable de disco USB.').
falla_info(466, 'PC', 'Secure Boot bloquea Linux', 'Desactivar Secure Boot en BIOS.').
falla_info(467, 'PC', 'CPU con pasta térmica en pines', 'Limpiar con cepillo y mucho alcohol.').
falla_info(468, 'PC', 'RAM en slot B1/B2 (Single)', 'Mover a A2/B2 para Dual Channel.').
falla_info(469, 'PC', 'GPU con soporte roto', 'Usar precintos para asegurar a chasis.').
falla_info(470, 'PC', 'Error de sistema Winload.efi', 'Reparar inicio con USB de instalación.').
falla_info(471, 'Laptop', 'HDD con sectores pendientes', 'Formatear a bajo nivel o cambiar.').
falla_info(472, 'Laptop', 'SSD M.2 se calienta mucho', 'Reducir carga de trabajo intensiva.').
falla_info(473, 'Laptop', 'Batería drena en reposo', 'Desactivar carga de móvil por USB.').
falla_info(474, 'Laptop', 'Carcasa con tornillos barridos', 'Usar extractor de tornillos pequeños.').
falla_info(475, 'Laptop', 'Wifi no ve canal 140', 'Cambiar canal de router a 36-48.').
falla_info(476, 'Laptop', 'Mouse BT pierde conexión', 'Desactivar ahorro de energía BT.').
falla_info(477, 'Laptop', 'Cargador de 45W en laptop de 90W', 'Usar cargador de vataje original.').
falla_info(478, 'Laptop', 'Pantalla con parpadeo blanco', 'Revisar cable LVDS en placa madre.').
falla_info(479, 'Laptop', 'Teclado no funciona tras update', 'Revertir driver en Administrador.').
falla_info(480, 'Laptop', 'Webcam con imagen en blanco', 'Falla de cable flex de video (Cámara).').
falla_info(481, 'PC', 'Ruido en micro por USB 3.0', 'Usar tarjeta de sonido externa.').
falla_info(482, 'PC', 'Fuente pita agudo (Whine)', 'Normal en fuentes baratas; cambiar.').
falla_info(483, 'PC', 'Olor a quemado (Goma)', 'Revisar aislantes de cables internos.').
falla_info(484, 'PC', 'Pitidos 1 largo 3 cortos', 'No se detecta tarjeta de video.').
falla_info(485, 'PC', 'Se apaga al conectar USB', 'Corto en puerto (No usarlo más).').
falla_info(486, 'PC', 'Fan de CPU ruidoso en frío', 'Rodamientos gastados; reemplazar.').
falla_info(487, 'PC', 'Internet cae al descargar', 'Falla de buffer en router o placa.').
falla_info(488, 'PC', 'No entra a BIOS con teclado BT', 'Usar teclado con cable USB.').
falla_info(489, 'PC', 'SD marca disco lleno', 'Verificar formato (FAT32 a NTFS).').
falla_info(490, 'PC', 'Audio suena con eco', 'Desactivar mezcla estéreo.').
falla_info(491, 'Laptop', 'Touchpad salta al tocar metal', 'Falta de tierra en el cargador.').
falla_info(492, 'Laptop', 'Se calienta mucho en Zoom', 'Bajar resolución de cámara.').
falla_info(493, 'Laptop', 'HDMI se corta al mover laptop', 'Puerto desoldado de la placa.').
falla_info(494, 'Laptop', 'Kensington no cierra bien', 'Limpiar ranura de seguridad.').
falla_info(495, 'Laptop', 'Wifi no ve redes de 6GHz', 'Laptop solo soporta Wifi 5 o 6.').
falla_info(496, 'Laptop', 'Audio suena distorsionado', 'Bocinas rotas por volumen alto.').
falla_info(497, 'Laptop', 'Batería carga hasta 50%', 'Cambiar modo en software de energía.').
falla_info(498, 'Laptop', 'Teclado se siente esponjoso', 'Derrame de líquido previo secado.').
falla_info(499, 'Laptop', 'Manchas oscuras en LCD', 'Humedad dentro de capas de pantalla.').
falla_info(500, 'Laptop', 'SSD NVMe no bootea', 'Habilitar modo AHCI/NVMe en BIOS.').

% --- hechos.pl: Lógica de Preguntas (401-500) ---

condicion(401, se_traba, '¿Error dice SMBus Controller?').
condicion(402, mouse_se_traba, '¿Dongle está junto a un disco USB 3.0?').
condicion(403, sin_imagen, '¿Cable HDMI tiene flechas de dirección?').
condicion(404, teclado_no_funciona, '¿Usa teclado de puerto circular viejo?').
condicion(405, pantallazo_azul, '¿Error dice L3_CACHE_ERROR?').
condicion(406, no_guarda_hora, '¿Hay polvo verde en el soporte de pila?').
condicion(407, ruido_extraño, '¿Gabinete vibra mucho al encender?').
condicion(408, reinicia_solo, '¿Vive en zona de mucha humedad?').
condicion(409, periferico_falla, '¿Puerto serial no recibe datos bien?').
condicion(410, usb_no_reconoce, '¿Ranura de SD tiene pines movidos?').
condicion(411, disco_lento, '¿SSD M.2 baja velocidad tras 5 min?').
condicion(412, se_traba, '¿PC se congela cada cierto tiempo fijo?').
condicion(413, ruido_extraño, '¿Escucha un silbido cerca del CPU?').
condicion(414, no_enciende, '¿Placa huele a quemado pero no se ve nada?').
condicion(415, no_enciende, '¿Vive cerca del mar?').
condicion(416, no_bootea, '¿Dice RAID Offline o Failed?').
condicion(417, sin_internet, '¿Hubo tormenta eléctrica ayer?').
condicion(418, imagen_distorsionada, '¿Rayas en pantalla solo al jugar?').
condicion(419, mouse_no_mueve, '¿Luz de mouse parpadea raro?').
condicion(420, no_enciende, '¿Movió un cuadrito de plástico en placa?').
condicion(421, no_inicia_sesion, '¿Sensor de huella se ve rayado?').
condicion(422, webcam_no_abre, '¿Antivirus avisó de bloqueo de cámara?').
condicion(423, audio_distorsionado, '¿Escucha su propia voz con retraso?').
condicion(424, ruido_extraño, '¿Pantalla se siente floja de un lado?').
condicion(425, parpadeo_pantalla, '¿Parpadea solo con brillo bajo?').
condicion(426, mouse_no_mueve, '¿Puntero se mueve solo a ratos?').
condicion(427, mouse_no_mueve, '¿Trackpad está más duro que antes?').
condicion(428, teclado_falla, '¿Presiona A y sale AX?').
condicion(429, usb_no_reconoce, '¿Slot de SD tiene restos de refresco?').
condicion(430, sin_internet, '¿Bios tiene Wifi deshabilitado?').
condicion(431, pantalla_negra, '¿Cree que la laptop está cerrada?').
condicion(432, audio_distorsionado, '¿Bocinas suenan muy roncas?').
condicion(433, usb_no_reconoce, '¿Usa cable de celular para el disco?').
condicion(434, disco_lento, '¿Laptop quema por abajo en el centro?').
condicion(435, teclado_falla, '¿Luces de teclas no prenden nunca?').
condicion(436, no_guarda_hora, '¿Dice CMOS Checksum Error al prender?').
condicion(437, no_bootea, '¿No puede activar Bitlocker?').
condicion(438, periferico_falla, '¿No lee tarjetas de empleado?').
condicion(439, señal_wifi_debil, '¿Se va el internet al cerrar la tapa?').
condicion(440, ruido_extraño, '¿Carcasa tiene grietas en esquinas?').
condicion(441, mouse_no_mueve, '¿Mouse inalámbrico no prende luz?').
condicion(442, se_apaga_solo, '¿PC se apaga al conectar un USB?').
condicion(443, no_entra_bios, '¿Pide clave de administrador de BIOS?').
condicion(444, ventilador_ruidoso, '¿Fan de CPU no gira pero hace ruido?').
condicion(445, imagen_distorsionada, '¿Imagen se ve muy roja o verde?').
condicion(446, no_bootea, '¿Disco duro no aparece como booteable?').
condicion(447, sin_internet, '¿Internet va a 10 Mbps máximo?').
condicion(448, ruido_extraño, '¿Disco duro hace clics rítmicos?').
condicion(449, no_enciende, '¿Luz de encendido no prende nunca?').
condicion(450, no_enciende, '¿Placa toca el metal del gabinete?').
condicion(451, imagen_distorsionada, '¿Ve manchas oscuras redondas?').
condicion(452, no_carga, '¿Cargador se sale solo?').
condicion(453, teclado_falla, '¿Teclas están muy duras de bajar?').
condicion(454, mouse_no_mueve, '¿No puede hacer clic derecho?').
condicion(455, no_enciende, '¿Se quedó sin batería hibernando?').
condicion(456, bluetooth_falla, '¿BT solo funciona a 10cm de laptop?').
condicion(457, imagen_distorsionada, '¿Pantalla se oscurece al desconectarla?').
condicion(458, no_carga, '¿Dice Batería no autorizada?').
condicion(459, usb_no_reconoce, '¿Puerto TB3 no reconoce discos?').
condicion(460, audio_distorsionado, '¿Audio pita al abrir programas?').
condicion(461, mouse_se_traba, '¿Mouse falla al conectar disco USB?').
condicion(462, sin_imagen, '¿Pantalla negra tras limpiar la PC?').
condicion(463, disco_no_detectado, '¿SSD M.2 no aparece en Windows?').
condicion(464, reinicia_solo, '¿Se reinicia si toca el gabinete?').
condicion(465, se_traba, '¿Se congela al meter un disco externo?').
condicion(466, no_bootea, '¿No puede arrancar desde USB Linux?').
condicion(467, no_enciende, '¿Puso mucha pasta térmica al CPU?').
condicion(468, pantallazo_azul, '¿RAM está en slots 1 y 2?').
condicion(469, ruido_extraño, '¿Tarjeta de video vibra o se cae?').
condicion(470, no_bootea, '¿Error 0xc000000e al arrancar?').
condicion(471, disco_lento, '¿Windows tarda 10 min en iniciar?').
condicion(472, se_traba, '¿SSD quema al tacto?').
condicion(473, bateria_dura_poco, '¿Batería baja mucho estando apagada?').
condicion(474, ruido_extraño, '¿Siente algo suelto al agitarla?').
condicion(475, sin_internet, '¿No ve el Wifi de su vecino/celular?').
condicion(476, mouse_se_traba, '¿Mouse tarda 2 seg en reaccionar?').
condicion(477, no_carga, '¿Carga muy lento y se calienta?').
condicion(478, parpadeo_pantalla, '¿Pantalla parpadea en blanco?').
condicion(479, teclado_falla, '¿Teclado murió tras actualizar?').
condicion(480, webcam_no_abre, '¿Imagen de cámara es puro blanco?').
condicion(481, ruido_en_audio, '¿Oye zumbido al grabar audio?').
condicion(482, ruido_extraño, '¿Fuente de poder pita agudo?').
condicion(483, no_enciende, '¿Huele a plástico quemado?').
condicion(484, no_da_imagen, '¿Pita 1 vez largo y 3 cortos?').
condicion(485, se_apaga_solo, '¿Se apaga al meter una memoria?').
condicion(486, ventilador_ruidoso, '¿Fan ruge al prender la PC?').
condicion(487, sin_internet, '¿Internet se corta al descargar mucho?').
condicion(488, no_entra_bios, '¿No puede pulsar F2/Del al inicio?').
condicion(489, usb_no_reconoce, '¿SD dice que no tiene espacio?').
condicion(490, audio_distorsionado, '¿Escucha eco en sus audífonos?').
condicion(491, mouse_no_mueve, '¿Touchpad falla con cargador puesto?').
condicion(492, laptop_caliente, '¿Ventilador ruge en videollamadas?').
condicion(493, hdmi_falla, '¿Imagen de TV se va si mueve la laptop?').
condicion(494, ruido_extraño, '¿Candado de seguridad se trabó?').
condicion(495, sin_internet, '¿No detecta redes de alta velocidad?').
condicion(496, audio_distorsionado, '¿Audio suena como bocina rota?').
condicion(497, no_carga, '¿No pasa del 50% u 80%?').
condicion(498, teclado_falla, '¿Teclas se sienten pegajosas?').
condicion(499, imagen_distorsionada, '¿Ve manchas oscuras en bordes?').
condicion(500, no_bootea, '¿SSD nuevo no arranca el sistema?').