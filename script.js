const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });

document.querySelectorAll('.reveal').forEach((element) => revealObserver.observe(element));

const countObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (!entry.isIntersecting) return;
    const element = entry.target;
    const target = Number(element.dataset.count);
    const suffix = element.dataset.suffix || '';
    const decimal = target % 1 !== 0;
    const start = performance.now();
    const duration = 1100;

    const tick = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const value = target * eased;
      element.textContent = `${decimal ? value.toFixed(1) : Math.round(value)}${suffix}`;
      if (progress < 1) requestAnimationFrame(tick);
    };

    requestAnimationFrame(tick);
    countObserver.unobserve(element);
  });
}, { threshold: 0.7 });

document.querySelectorAll('[data-count]').forEach((element) => countObserver.observe(element));

const toggle = document.querySelector('.menu-toggle');
const nav = document.querySelector('.site-nav');
if (toggle && nav) {
  const setMenuOpen = (open) => {
    nav.classList.toggle('open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? '关闭主导航' : '打开主导航');
    toggle.textContent = open ? '关闭' : '菜单';
  };

  toggle.addEventListener('click', () => {
    setMenuOpen(!nav.classList.contains('open'));
  });

  nav.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => {
    setMenuOpen(false);
  }));

  document.addEventListener('click', (event) => {
    if (!nav.classList.contains('open') || nav.contains(event.target) || toggle.contains(event.target)) return;
    setMenuOpen(false);
  });

  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape' || !nav.classList.contains('open')) return;
    setMenuOpen(false);
    toggle.focus();
  });
}

const navLinks = nav ? [...nav.querySelectorAll('a[href^="#"]')] : [];
const sectionMap = navLinks
  .map((link) => ({ link, section: document.querySelector(link.getAttribute('href')) }))
  .filter((item) => item.section);

const sectionObserver = new IntersectionObserver((entries) => {
  const visible = entries
    .filter((entry) => entry.isIntersecting)
    .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
  if (!visible) return;
  navLinks.forEach((link) => link.classList.remove('active'));
  sectionMap.find((item) => item.section === visible.target)?.link.classList.add('active');
}, { rootMargin: '-24% 0px -58% 0px', threshold: [0, 0.2, 0.5] });

sectionMap.forEach(({ section }) => sectionObserver.observe(section));

document.querySelectorAll('a[aria-disabled="true"]').forEach((link) => {
  link.addEventListener('click', (event) => event.preventDefault());
});

document.querySelectorAll('[data-music-player]').forEach((player) => {
  const audio = player.querySelector('[data-music-source]');
  const button = player.querySelector('.music-player__button');
  const label = player.querySelector('[data-music-label]');
  const hint = player.querySelector('.music-player__hint');
  const playIcon = player.querySelector('.music-player__play-icon');
  const pauseIcon = player.querySelector('.music-player__pause-icon');
  if (!audio || !button) return;

  const setPlaybackState = (playing) => {
    player.classList.toggle('is-playing', playing);
    button.setAttribute('aria-pressed', String(playing));
    button.setAttribute('aria-label', playing ? '暂停背景音乐' : '播放背景音乐');
    if (label) label.textContent = playing ? '暂停背景音乐' : '播放背景音乐';
    if (hint) hint.textContent = playing ? '播放中，点击暂停' : '听一首歌';
    if (playIcon) playIcon.hidden = playing;
    if (pauseIcon) pauseIcon.hidden = !playing;
  };

  button.addEventListener('click', async () => {
    if (audio.paused) {
      if (audio.ended) audio.currentTime = 0;
      try {
        await audio.play();
      } catch (error) {
        setPlaybackState(false);
      }
    } else {
      audio.pause();
    }
  });

  audio.addEventListener('play', () => setPlaybackState(true));
  audio.addEventListener('pause', () => setPlaybackState(false));
  audio.addEventListener('ended', () => setPlaybackState(false));
});

const storyDialog = document.querySelector('#childhood-story-dialog');
const storyTrigger = document.querySelector('.story-note-trigger');
if (storyDialog && storyTrigger) {
  const storyNotes = [...storyDialog.querySelectorAll('[data-story-note]')];
  const storyNext = storyDialog.querySelector('.story-dialog__next');
  const storyProgress = storyDialog.querySelector('#story-dialog-progress');
  const storyCloseControls = storyDialog.querySelectorAll('[data-story-dialog-close]');
  let storyIndex = 0;

  const showStoryNote = (index) => {
    storyIndex = index % storyNotes.length;
    storyNotes.forEach((note, noteIndex) => { note.hidden = noteIndex !== storyIndex; });
    storyProgress.textContent = `第 ${storyIndex + 1} 张，共 ${storyNotes.length} 张`;
    storyNext.innerHTML = storyIndex === storyNotes.length - 1 ? '从头再看 <span aria-hidden="true">↺</span>' : '翻到下一张 <span aria-hidden="true">→</span>';
  };

  const closeStoryDialog = () => {
    storyDialog.classList.remove('is-open');
    storyDialog.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('story-dialog-open');
    storyTrigger.focus();
  };

  storyTrigger.addEventListener('click', () => {
    showStoryNote(0);
    storyDialog.classList.add('is-open');
    storyDialog.setAttribute('aria-hidden', 'false');
    document.body.classList.add('story-dialog-open');
    storyDialog.querySelector('.story-dialog__close').focus();
  });

  storyNext.addEventListener('click', () => showStoryNote(storyIndex + 1));
  storyCloseControls.forEach((control) => control.addEventListener('click', closeStoryDialog));
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && storyDialog.classList.contains('is-open')) closeStoryDialog();
    if (event.key !== 'Tab' || !storyDialog.classList.contains('is-open')) return;
    const focusable = [...storyDialog.querySelectorAll('button:not([disabled]), [href], [tabindex]:not([tabindex="-1"])')].filter((element) => !element.hidden);
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (!first || !last) return;
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
    if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
  });
}

document.querySelectorAll('[data-media-stack]').forEach((posterStack) => {
  const showcase = posterStack.closest('.stack-showcase');
  const posterNext = showcase?.querySelector('.poster-next');
  const posterCounter = showcase?.querySelector('.poster-counter');
  if (!posterNext || !posterCounter) return;
  let posterPosition = 1;
  const totalPosters = posterStack.querySelectorAll('.poster-card').length;
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const updatePosterStack = () => {
    [...posterStack.children].forEach((card, index) => {
      card.style.setProperty('--stack-index', index);
      card.style.zIndex = String(totalPosters - index);
      card.tabIndex = index === 0 ? 0 : -1;
      card.setAttribute('aria-hidden', String(index !== 0));
    });
    posterCounter.textContent = `${String(posterPosition).padStart(2, '0')} / ${String(totalPosters).padStart(2, '0')}`;
  };

  const showNextPoster = () => {
    const current = posterStack.querySelector('.poster-card');
    if (!current || current.classList.contains('is-leaving')) return;
    current.classList.add('is-leaving');
    window.setTimeout(() => {
      current.classList.remove('is-leaving');
      posterStack.append(current);
      posterPosition = posterPosition % totalPosters + 1;
      updatePosterStack();
    }, prefersReducedMotion ? 0 : 260);
  };

  posterNext.addEventListener('click', showNextPoster);
  posterStack.addEventListener('click', (event) => {
    if (event.target.closest('.poster-card') === posterStack.firstElementChild) showNextPoster();
  });
  updatePosterStack();
});
