/* ------------------------------------------------------------------
   Motor dos quizzes do Grupo de Estudos.

   Cada arquivo `quiz_dia_XX.html` define um objeto global `QUIZ`:

     const QUIZ = {
       dia: "Dia 04",
       titulo: "Tema do encontro",
       chave: "quiz_dia_04",        // usada para guardar o recorde no navegador
       perguntas: [ ... ]
     };

   Tipos de pergunta suportados:

     { tipo: "vf",        enunciado, resposta: true|false, explicacao }
     { tipo: "multipla",  enunciado, opcoes: [...], correta: <índice>, explicacao }
     { tipo: "completar", enunciado, respostas: [...aceitas], explicacao }
     { tipo: "ordenar",   enunciado, itens: [...na ordem correta], explicacao }
     { tipo: "associar",  enunciado, pares: [[esquerda, direita], ...], explicacao }

   Nos enunciados, `crase` vira código e **asterisco duplo** vira negrito.
------------------------------------------------------------------- */

(function () {
  "use strict";

  const NOME_TIPO = {
    vf: "Verdadeiro ou falso",
    multipla: "Múltipla escolha",
    completar: "Complete a palavra",
    ordenar: "Coloque em ordem",
    associar: "Associe as colunas"
  };

  let palco, btnPrincipal, btnSecundario, progresso, contador, placarAcertos;
  let config = null;
  let fila = [];
  let indice = 0;
  let acertos = 0;
  let erradas = [];
  let verificada = false;
  let obterResposta = null;

  function escapar(texto) {
    return String(texto).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function fmt(texto) {
    return escapar(texto)
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  }

  function embaralhar(lista) {
    const copia = lista.slice();
    for (let i = copia.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [copia[i], copia[j]] = [copia[j], copia[i]];
    }
    return copia;
  }

  function normalizar(texto) {
    return String(texto)
      .trim()
      .toLowerCase()
      .normalize("NFD")
      .replace(/[̀-ͯ]/g, "")
      .replace(/[^a-z0-9]/g, "");
  }

  function montarEsqueleto() {
    const wrap = document.createElement("div");
    wrap.className = "wrap";
    wrap.innerHTML =
      "<header>" +
        '<p class="kicker">Grupo de Estudos em IA Generativa · Navi Hub &amp; DataLakers</p>' +
        "<h1>" + escapar(config.dia) + " — " + escapar(config.titulo) + "</h1>" +
        '<div class="barra"><div id="progresso"></div></div>' +
        '<div class="status"><span id="contador"></span><span id="acertos"></span></div>' +
      "</header>" +
      '<main id="palco"></main>';

    const rodape = document.createElement("div");
    rodape.className = "rodape";
    rodape.innerHTML =
      '<div class="wrap">' +
        '<button type="button" class="secundaria oculto" id="btn-secundario"></button>' +
        '<button type="button" class="principal" id="btn-principal">Verificar</button>' +
      "</div>";

    document.body.append(wrap, rodape);

    palco = document.getElementById("palco");
    btnPrincipal = document.getElementById("btn-principal");
    btnSecundario = document.getElementById("btn-secundario");
    progresso = document.getElementById("progresso");
    contador = document.getElementById("contador");
    placarAcertos = document.getElementById("acertos");

    btnPrincipal.addEventListener("click", function () {
      if (obterResposta === null) iniciar(config.perguntas);
      else if (verificada) avancar();
      else verificar();
    });

    btnSecundario.addEventListener("click", function () {
      iniciar(erradas.slice());
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !btnPrincipal.disabled) {
        e.preventDefault();
        btnPrincipal.click();
      }
    });
  }

  function iniciar(perguntas) {
    fila = perguntas;
    indice = 0;
    acertos = 0;
    erradas = [];
    render();
  }

  function render() {
    verificada = false;
    const p = fila[indice];

    progresso.style.width = (indice / fila.length) * 100 + "%";
    contador.textContent = "Pergunta " + (indice + 1) + " de " + fila.length;
    placarAcertos.textContent = acertos + (acertos === 1 ? " acerto" : " acertos");

    const card = document.createElement("section");
    card.className = "card";
    card.innerHTML =
      '<span class="tipo">' + NOME_TIPO[p.tipo] + "</span>" +
      '<p class="enunciado">' + fmt(p.enunciado) + "</p>";

    const area = document.createElement("div");
    card.appendChild(area);
    palco.replaceChildren(card);

    const construtores = {
      vf: montarVF,
      multipla: montarMultipla,
      completar: montarCompletar,
      ordenar: montarOrdenar,
      associar: montarAssociar
    };
    obterResposta = construtores[p.tipo](area, p);

    btnPrincipal.textContent = "Verificar";
    btnPrincipal.disabled = true;
    btnSecundario.classList.add("oculto");
  }

  function liberarVerificacao(liberado) {
    btnPrincipal.disabled = !liberado;
  }

  function criarOpcao(texto, pai) {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "opcao";
    b.setAttribute("aria-pressed", "false");
    b.innerHTML = '<span class="marca"></span><span>' + fmt(texto) + "</span>";
    pai.appendChild(b);
    return b;
  }

  function montarVF(area, p) {
    const grade = document.createElement("div");
    grade.className = "opcoes vf";
    area.appendChild(grade);

    let escolha = null;
    const botoes = [
      { rotulo: "Verdadeiro", valor: true },
      { rotulo: "Falso", valor: false }
    ].map(function (op) {
      const b = criarOpcao(op.rotulo, grade);
      b.addEventListener("click", function () {
        escolha = op.valor;
        botoes.forEach(function (outro) {
          outro.el.setAttribute("aria-pressed", String(outro.valor === escolha));
        });
        liberarVerificacao(true);
      });
      return { el: b, valor: op.valor };
    });

    return function () {
      botoes.forEach(function (b) {
        b.el.disabled = true;
        if (b.valor === p.resposta) b.el.classList.add("certa");
        else if (b.valor === escolha) b.el.classList.add("errada");
      });
      return escolha === p.resposta;
    };
  }

  function montarMultipla(area, p) {
    const grade = document.createElement("div");
    grade.className = "opcoes";
    area.appendChild(grade);

    const opcoes = embaralhar(
      p.opcoes.map(function (texto, i) {
        return { texto: texto, certa: i === p.correta };
      })
    );

    let escolha = null;
    const botoes = opcoes.map(function (op) {
      const b = criarOpcao(op.texto, grade);
      b.addEventListener("click", function () {
        escolha = op;
        botoes.forEach(function (outro) {
          outro.el.setAttribute("aria-pressed", String(outro.op === escolha));
        });
        liberarVerificacao(true);
      });
      return { el: b, op: op };
    });

    return function () {
      botoes.forEach(function (b) {
        b.el.disabled = true;
        if (b.op.certa) b.el.classList.add("certa");
        else if (b.op === escolha) b.el.classList.add("errada");
      });
      return Boolean(escolha && escolha.certa);
    };
  }

  function montarCompletar(area, p) {
    const campo = document.createElement("input");
    campo.type = "text";
    campo.autocomplete = "off";
    campo.autocapitalize = "off";
    campo.spellcheck = false;
    campo.placeholder = "Digite sua resposta";
    campo.setAttribute("aria-label", "Resposta");
    area.appendChild(campo);

    const dica = document.createElement("p");
    dica.className = "dica";
    dica.textContent = "Acentos e maiúsculas não são considerados.";
    area.appendChild(dica);

    campo.addEventListener("input", function () {
      liberarVerificacao(campo.value.trim().length > 0);
    });
    campo.focus();

    return function () {
      campo.disabled = true;
      const certo = p.respostas.some(function (r) {
        return normalizar(r) === normalizar(campo.value);
      });
      campo.style.borderColor = certo ? "var(--ok)" : "var(--err)";
      if (!certo) {
        const correta = document.createElement("p");
        correta.className = "dica";
        correta.innerHTML = "Resposta correta: <strong>" + fmt(p.respostas[0]) + "</strong>";
        area.appendChild(correta);
      }
      return certo;
    };
  }

  function montarOrdenar(area, p) {
    const lista = document.createElement("div");
    lista.className = "opcoes";
    area.appendChild(lista);

    const escolhidos = [];
    const botoes = embaralhar(
      p.itens.map(function (texto, i) {
        return { texto: texto, posicao: i };
      })
    ).map(function (item) {
      const b = criarOpcao(item.texto, lista);
      b.addEventListener("click", function () {
        const jaEscolhido = escolhidos.indexOf(item);
        if (jaEscolhido >= 0) escolhidos.splice(jaEscolhido, 1);
        else escolhidos.push(item);
        atualizar();
      });
      return { el: b, item: item };
    });

    function atualizar() {
      botoes.forEach(function (b) {
        const pos = escolhidos.indexOf(b.item);
        b.el.setAttribute("aria-pressed", String(pos >= 0));
        b.el.querySelector(".marca").textContent = pos >= 0 ? String(pos + 1) : "";
      });
      liberarVerificacao(escolhidos.length === p.itens.length);
    }

    return function () {
      const certo = escolhidos.every(function (item, i) {
        return item.posicao === i;
      });
      botoes.forEach(function (b) {
        b.el.disabled = true;
        const pos = escolhidos.indexOf(b.item);
        b.el.classList.add(pos === b.item.posicao ? "certa" : "errada");
      });
      if (!certo) {
        const ordem = document.createElement("p");
        ordem.className = "dica";
        ordem.innerHTML = "Ordem correta: " + p.itens.map(function (t, i) {
          return (i + 1) + ". " + fmt(t);
        }).join(" · ");
        area.appendChild(ordem);
      }
      return certo;
    };
  }

  function montarAssociar(area, p) {
    const grade = document.createElement("div");
    grade.className = "colunas";
    area.appendChild(grade);

    const colunaEsq = document.createElement("div");
    colunaEsq.className = "opcoes";
    const colunaDir = document.createElement("div");
    colunaDir.className = "opcoes";
    grade.append(colunaEsq, colunaDir);

    const ligacoes = new Map();
    let selecionadoEsq = null;

    const esquerda = p.pares.map(function (par, i) {
      const b = criarOpcao(par[0], colunaEsq);
      b.addEventListener("click", function () {
        if (ligacoes.has(i)) ligacoes.delete(i);
        selecionadoEsq = selecionadoEsq === i ? null : i;
        atualizar();
      });
      return b;
    });

    const direita = embaralhar(
      p.pares.map(function (par, i) {
        return { texto: par[1], indice: i };
      })
    ).map(function (item) {
      const b = criarOpcao(item.texto, colunaDir);
      b.addEventListener("click", function () {
        for (const [esq, dir] of ligacoes) {
          if (dir === item.indice) ligacoes.delete(esq);
        }
        if (selecionadoEsq !== null) {
          ligacoes.set(selecionadoEsq, item.indice);
          selecionadoEsq = null;
        }
        atualizar();
      });
      return { el: b, item: item };
    });

    function indiceLigacao(esq) {
      return Array.from(ligacoes.keys()).sort(function (a, b) { return a - b; }).indexOf(esq) + 1;
    }

    function atualizar() {
      esquerda.forEach(function (b, i) {
        const ligado = ligacoes.has(i);
        b.setAttribute("aria-pressed", String(ligado || selecionadoEsq === i));
        b.querySelector(".marca").textContent = ligado ? String(indiceLigacao(i)) : "";
      });
      direita.forEach(function (b) {
        let numero = "";
        for (const [esq, dir] of ligacoes) {
          if (dir === b.item.indice) numero = String(indiceLigacao(esq));
        }
        b.el.setAttribute("aria-pressed", String(numero !== ""));
        b.el.querySelector(".marca").textContent = numero;
      });
      liberarVerificacao(ligacoes.size === p.pares.length);
    }

    return function () {
      let certo = true;
      esquerda.forEach(function (b, i) {
        b.disabled = true;
        const acertou = ligacoes.get(i) === i;
        b.classList.add(acertou ? "certa" : "errada");
        if (!acertou) certo = false;
      });
      direita.forEach(function (b) { b.el.disabled = true; });
      if (!certo) {
        const gabarito = document.createElement("p");
        gabarito.className = "dica";
        gabarito.innerHTML = "Pares corretos: " + p.pares.map(function (par) {
          return fmt(par[0]) + " → " + fmt(par[1]);
        }).join(" · ");
        area.appendChild(gabarito);
      }
      return certo;
    };
  }

  function mostrarFeedback(certo, explicacao) {
    const box = document.createElement("div");
    box.className = "feedback " + (certo ? "ok" : "erro");
    box.setAttribute("role", "status");
    box.innerHTML =
      "<strong>" + (certo ? "✅ Correto!" : "❌ Ainda não") + "</strong>" +
      "<p>" + fmt(explicacao) + "</p>";
    palco.querySelector(".card").appendChild(box);
  }

  function verificar() {
    const p = fila[indice];
    const certo = obterResposta();
    if (certo) acertos++;
    else erradas.push(p);

    mostrarFeedback(certo, p.explicacao);
    placarAcertos.textContent = acertos + (acertos === 1 ? " acerto" : " acertos");
    verificada = true;
    btnPrincipal.textContent = indice + 1 < fila.length ? "Continuar" : "Ver resultado";
    btnPrincipal.disabled = false;
  }

  function avancar() {
    indice++;
    if (indice < fila.length) render();
    else finalizar();
  }

  function lerRecorde() {
    try {
      const salvo = Number(localStorage.getItem(config.chave));
      return Number.isFinite(salvo) ? salvo : 0;
    } catch (e) {
      return 0;
    }
  }

  function salvarRecorde(percentual) {
    try {
      if (percentual > lerRecorde()) localStorage.setItem(config.chave, String(percentual));
    } catch (e) {
      /* localStorage bloqueado (janela anônima, por exemplo) — segue sem recorde */
    }
  }

  function finalizar() {
    const total = fila.length;
    const percentual = Math.round((acertos / total) * 100);
    const recordeAnterior = lerRecorde();
    salvarRecorde(percentual);

    progresso.style.width = "100%";
    contador.textContent = "Quiz concluído";

    let frase;
    if (percentual >= 90) frase = "Conteúdo dominado. Pode seguir para o próximo encontro tranquilo.";
    else if (percentual >= 70) frase = "Boa base! Revise os pontos abaixo antes do próximo encontro.";
    else if (percentual >= 50) frase = "Deu para pegar o essencial, mas vale reler o roteiro do dia.";
    else frase = "Vale refazer as atividades do dia com calma e tentar de novo.";

    const card = document.createElement("section");
    card.className = "card";
    card.innerHTML =
      '<div class="placar">' +
        '<p class="nota">' + acertos + "/" + total + "</p>" +
        '<p class="frase">' + percentual + "% de acerto · " + escapar(frase) + "</p>" +
      "</div>" +
      (recordeAnterior > 0 ? '<p class="recorde">Seu melhor resultado anterior neste quiz: ' + recordeAnterior + "%</p>" : "");

    if (erradas.length) {
      const bloco = document.createElement("div");
      bloco.className = "erros";
      bloco.innerHTML =
        "<h2>Para revisar (" + erradas.length + "):</h2><ul>" +
        erradas.map(function (p) { return "<li>" + fmt(p.enunciado) + "</li>"; }).join("") +
        "</ul>";
      card.appendChild(bloco);
    }

    palco.replaceChildren(card);

    btnPrincipal.textContent = "Refazer tudo";
    btnPrincipal.disabled = false;
    if (erradas.length) {
      btnSecundario.textContent = "Refazer só os erros (" + erradas.length + ")";
      btnSecundario.classList.remove("oculto");
    } else {
      btnSecundario.classList.add("oculto");
    }
    verificada = false;
    obterResposta = null;
  }

  // `const QUIZ` declarado no HTML vive no escopo léxico global, e não em `window`.
  const definido = typeof QUIZ !== "undefined" ? QUIZ : window.QUIZ;

  if (!definido || !Array.isArray(definido.perguntas) || !definido.perguntas.length) {
    document.body.innerHTML =
      '<div class="wrap"><section class="card"><p class="enunciado">Quiz não carregado.</p>' +
      "<p>Este arquivo precisa definir o objeto <code>QUIZ</code> antes de incluir o <code>quiz.js</code>.</p></section></div>";
    return;
  }

  config = definido;
  document.title = "Quiz — " + config.dia + " | " + config.titulo;
  montarEsqueleto();
  iniciar(config.perguntas);
})();