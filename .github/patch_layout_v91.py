from pathlib import Path

path = Path('Gestao_de_Projetos.html')
html = path.read_text(encoding='utf-8')
html = html.replace('<title>CSC Gestão de Projetos | v90</title>', '<title>CSC Gestão de Projetos | v91</title>', 1)

css = r'''
  <style data-csc-layout-v91>
    #cadastrosPage .registration-item-main { min-width: 0 !important; }
    #cadastrosPage .registration-item-meta {
      display: flex !important;
      align-items: center !important;
      justify-content: flex-start !important;
      flex-wrap: wrap !important;
      gap: 10px 14px !important;
      margin-top: 9px !important;
    }
    #cadastrosPage .registration-item-meta > span:first-child {
      flex: 0 1 auto !important;
      min-width: 0 !important;
      font-size: .76rem !important;
      line-height: 1.25 !important;
      font-weight: 650 !important;
    }
    #cadastrosPage .registration-item-meta .status {
      position: static !important;
      flex: 0 0 auto !important;
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      width: auto !important;
      min-width: 92px !important;
      min-height: 27px !important;
      padding: 4px 10px !important;
      margin: 0 !important;
      border-radius: 999px !important;
      font-size: .76rem !important;
      line-height: 1.15 !important;
      font-weight: 800 !important;
      text-align: center !important;
      white-space: normal !important;
    }
    #overviewPage .projects-panel .project-cell,
    #overviewPage .projects-panel td:first-child .project-cell {
      min-width: 0 !important;
      align-items: center !important;
    }
    #overviewPage .projects-panel .project-cell strong,
    #overviewPage .projects-panel td:first-child strong {
      display: -webkit-box !important;
      -webkit-box-orient: vertical !important;
      -webkit-line-clamp: 2 !important;
      white-space: normal !important;
      overflow: hidden !important;
      text-overflow: ellipsis !important;
      overflow-wrap: anywhere !important;
      word-break: break-word !important;
      max-width: none !important;
      line-height: 1.28 !important;
      font-size: .82rem !important;
    }
    #overviewPage .projects-panel tbody tr { height: auto !important; min-height: 70px !important; }
    #overviewPage .projects-panel tbody td {
      padding-top: 10px !important;
      padding-bottom: 10px !important;
      vertical-align: middle !important;
    }
    @media (max-width: 1180px) {
      #overviewPage .projects-panel .project-cell strong,
      #overviewPage .projects-panel td:first-child strong { -webkit-line-clamp: 3 !important; }
    }
  </style>
'''
if 'data-csc-layout-v91' not in html:
    html = html.replace('</head>', css + '\n</head>', 1)
path.write_text(html, encoding='utf-8')
