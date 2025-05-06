const fields = ['HoursOfStudyPerDay','HoursOfSleep','ScreenTimeHours','PhysicalActivityHours']
  .map(id => document.querySelector(`[name="${id}"]`));
const warning = document.getElementById('hoursWarning');
fields.forEach(f => f && f.addEventListener('input', () => {
  const sum = fields.reduce((a,el) => a + parseFloat(el.value||0), 0);
  warning?.classList.toggle('hidden', sum <= 24);
}));
