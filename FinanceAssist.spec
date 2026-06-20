# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets'), ('translations.json', '.')],
    hiddenimports=['views.resumo_financeiro_view', 'views.transacao_view', 'views.meta_view', 'views.lista_categorias_view', 'views.relatorio_view', 'views.favorecido_view', 'views.agendamento_view', 'views.perfil_view', 'views.gerenciamento_usuarios_view', 'views.configuracoes_view', 'views.backup_view'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FinanceAssist',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FinanceAssist',
)
