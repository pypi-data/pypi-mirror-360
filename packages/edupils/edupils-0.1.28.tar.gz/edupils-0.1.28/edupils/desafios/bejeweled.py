import numpy as np

dicionario_emojis = {
    # coracoes
    ('coracao', 'azul'): '💙',  # U+1F499
    ('coracao', 'amarelo'): '💛',  # U+1F49B
    ('coracao', 'verde'): '💚',  # U+1F49A
    ('coracao', 'roxo'): '💜',  # U+1F49C

    # quadrados
    ('quadrado', 'azul'): '🟦',  # U+1F7E6
    ('quadrado', 'amarelo'): '🟨',  # U+1F7E8
    ('quadrado', 'verde'): '🟩',  # U+1F7E9
    ('quadrado', 'roxo'): '🟪',  # U+1F7EA

    # circulos
    ('circulo', 'azul'): '🔵',  # U+1F535
    ('circulo', 'amarelo'): '🟡',  # U+1F7E1
    ('circulo', 'verde'): '🟢',  # U+1F7E2
    ('circulo', 'roxo'): '🟣',  # U+1F7E3
}


def tabela_emojis(largura=12, altura=8):
    emojis_idx = np.random.choice(len(dicionario_emojis), size=(altura,largura), replace=True).tolist()
    idx = list(dicionario_emojis.keys())
    
    emojis_descricao = [[idx[shape_id] for shape_id in row] for row in emojis_idx]
    emojis = "\n".join(
        [
            "".join([dicionario_emojis[emo_desc] for emo_desc in row]) 
            for row in emojis_descricao
        ]
    )

    return emojis, emojis_descricao

# Example of accessing an emoji
emojis, emojis_descricao = (tabela_emojis())

print(emojis)
