/** Always visible (Project Guide §5): decision support, not a diagnosis. */
export function DisclaimerBanner() {
  return (
    <div className="disclaimer" role="note" aria-label="Disclaimer">
      <strong>Decision support, not a diagnosis.</strong> Not a medical device. Thresholds are documented demo rules.
    </div>
  );
}
