"""
Detección de situaciones de riesgo: ideación suicida, autolesión, crisis de pánico severa.

Capa completamente independiente del clasificador ML.
Usa patrones regex que cubren conjugaciones y variantes lingüísticas,
con verificación de negación por ventana de tokens anterior al match.

Niveles:
  alto  → ideación suicida, ideación pasiva o autolesión
  medio → crisis severa de ansiedad o colapso emocional
  bajo  → sin señales de riesgo detectadas
"""

import re
from typing import Dict, List, Tuple

# (patrón compilado, tipo, nivel)
_CRISIS_PATTERNS: List[Tuple[re.Pattern, str, str]] = [

    # ── RIESGO ALTO: Ideación suicida directa ─────────────────────────────
    (re.compile(r'quier[oa]\s+morir', re.I | re.U),
     'ideacion_suicida', 'alto'),

    (re.compile(r'no\s+quier[oa]\s+(seguir\s+)?(vivir|viviendo|existir)', re.I | re.U),
     'ideacion_suicida', 'alto'),

    (re.compile(r'no\s+querer\s+seguir\s+viviendo', re.I | re.U),
     'ideacion_suicida', 'alto'),

    (re.compile(r'(quitarme|acabar\s+con\s+mi)\s+la?\s*vida', re.I | re.U),
     'ideacion_suicida', 'alto'),

    (re.compile(r'suicidar(me|se|nos)', re.I | re.U),
     'ideacion_suicida', 'alto'),

    (re.compile(r'acabar\s+con\s+todo(\s+esto)?', re.I | re.U),
     'ideacion_suicida', 'alto'),

    (re.compile(r'pensar?\s+en\s+(el\s+)?suicidio', re.I | re.U),
     'ideacion_suicida', 'alto'),

    (re.compile(r'pensamientos\s+suicidas', re.I | re.U),
     'ideacion_suicida', 'alto'),

    (re.compile(r'pensamientos\s+(de\s+muerte|relacionados\s+con\s+(morir|la\s+muerte))',
                re.I | re.U),
     'ideacion_suicida', 'alto'),

    # Eufemismos — lenguaje indirecto frecuente clínicamente
    (re.compile(r'dejar\s+de\s+existir', re.I | re.U),
     'ideacion_suicida', 'alto'),

    (re.compile(r'dejar\s+de\s+estar\s+(aquí|acá)', re.I | re.U),
     'ideacion_suicida', 'alto'),

    (re.compile(r'escapar\s+(definitivamente|para\s+siempre|de\s+todo(\s+esto)?)',
                re.I | re.U),
     'ideacion_suicida', 'alto'),

    (re.compile(r'descansar\s+para\s+siempre', re.I | re.U),
     'ideacion_suicida', 'alto'),

    (re.compile(r'(ya\s+)?no\s+(tiene\s+sentido|vale\s+la\s+pena)\s+seguir',
                re.I | re.U),
     'ideacion_suicida', 'alto'),

    (re.compile(r'seguir\s+(ya\s+)?no\s+tiene\s+sentido', re.I | re.U),
     'ideacion_suicida', 'alto'),

    (re.compile(r'(ya\s+)?no\s+quier[oa]\s+despertar', re.I | re.U),
     'ideacion_suicida', 'alto'),

    (re.compile(r'dormir\s+y\s+no\s+despertar', re.I | re.U),
     'ideacion_suicida', 'alto'),

    (re.compile(r'desaparecer\s+para\s+siempre', re.I | re.U),
     'ideacion_suicida', 'alto'),

    # ── RIESGO ALTO: Autolesión ────────────────────────────────────────────
    (re.compile(r'(hacerme|lastimarme|cortarme|herirme|dañarme)(\s+daño)?',
                re.I | re.U),
     'autolesion', 'alto'),

    (re.compile(r'autolesion(arme|arse|arlos)?', re.I | re.U),
     'autolesion', 'alto'),

    # ── RIESGO ALTO: Ideación pasiva ──────────────────────────────────────
    # Percibirse como carga — patrón muy común y clínicamente relevante
    (re.compile(r'mejor\s+(que\s+no|si\s+no)\s+(existiera|estuviera|viviera)',
                re.I | re.U),
     'ideacion_pasiva', 'alto'),

    (re.compile(r'mejor\s+sin\s+mí', re.I | re.U),
     'ideacion_pasiva', 'alto'),

    (re.compile(r'(soy|siendo|me\s+siento)\s+una\s+carga', re.I | re.U),
     'ideacion_pasiva', 'alto'),

    (re.compile(r'(todos\s+)?estarían\s+mejor\s+sin\s+mí', re.I | re.U),
     'ideacion_pasiva', 'alto'),

    (re.compile(r'mi\s+ausencia\s+.{0,40}(mejor|impacto|importar)', re.I | re.U | re.S),
     'ideacion_pasiva', 'alto'),

    (re.compile(r'nadie\s+(me\s+)?extrañaría', re.I | re.U),
     'ideacion_pasiva', 'alto'),

    # ── RIESGO MEDIO: Crisis severa de ansiedad ───────────────────────────
    (re.compile(r'ataque\s+de\s+(pánico|panico|ansiedad)', re.I | re.U),
     'crisis_panico', 'medio'),

    (re.compile(
        r'no\s+(puedo|logro)\s+respirar(\s+de(l?\s+)?(pánico|panico|ansiedad|nervios))?',
        re.I | re.U),
     'crisis_panico', 'medio'),

    (re.compile(r'siento\s+que\s+(me\s+muero|voy\s+a\s+morir|me\s+voy\s+a\s+desmayar)',
                re.I | re.U),
     'crisis_panico', 'medio'),

    (re.compile(r'(pierdo|perdiendo)\s+el\s+control\s+completamente', re.I | re.U),
     'perdida_control', 'medio'),

    (re.compile(r'(ya\s+)?no\s+(puedo|aguanto|soporto)\s+más(\s+con\s+esto)?',
                re.I | re.U),
     'colapso', 'medio'),

    (re.compile(r'me\s+estoy\s+volviendo\s+loc[ao]', re.I | re.U),
     'descompensacion', 'medio'),

    (re.compile(r'no\s+(puedo|logro)\s+seguir\s+así', re.I | re.U),
     'colapso', 'medio'),
]

_NEGATION_RE = re.compile(
    r'\b(no|nunca|jamás|jamas|tampoco|ni|sin|nada)\b',
    re.I | re.U
)


def _has_negation_before(text: str, match_start: int, window_words: int = 5) -> bool:
    """
    Verifica si hay una palabra de negación en las `window_words` palabras
    inmediatamente anteriores al inicio del match.
    """
    preceding = text[:match_start]
    tokens = re.findall(r'\b[\wáéíóúüñ]+\b', preceding.lower())
    window = tokens[-window_words:]
    return bool(_NEGATION_RE.search(' '.join(window)))


def detect_risk(text: str) -> Dict:
    """
    Analiza el texto en busca de señales de riesgo clínico usando patrones regex.

    Cubre conjugaciones, variantes de género e indirecciones lingüísticas.
    Aplica verificación de negación antes de cada coincidencia.

    Args:
        text: Texto del paciente (respuestas concatenadas)

    Returns:
        {
            'nivel_riesgo': 'alto' | 'medio' | 'bajo',
            'requiere_atencion': bool,
            'señales_detectadas': [{'tipo': str, 'frase': str, 'nivel': str}]
        }
    """
    señales: List[Dict] = []

    for pattern, tipo, nivel in _CRISIS_PATTERNS:
        match = pattern.search(text)
        if match and not _has_negation_before(text, match.start()):
            señales.append({
                'tipo': tipo,
                'frase': match.group(0),
                'nivel': nivel,
            })

    if any(s['nivel'] == 'alto' for s in señales):
        nivel_riesgo = 'alto'
        requiere_atencion = True
    elif any(s['nivel'] == 'medio' for s in señales):
        nivel_riesgo = 'medio'
        requiere_atencion = True
    else:
        nivel_riesgo = 'bajo'
        requiere_atencion = False

    return {
        'nivel_riesgo': nivel_riesgo,
        'requiere_atencion': requiere_atencion,
        'señales_detectadas': señales,
    }
