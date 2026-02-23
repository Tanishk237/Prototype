import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def generate_pdf_report(result, output_path="data/output/review_analysis_report.pdf"):
    """
    Generates comprehensive PDF report with stats, outliers, and influential reviews.
    """
    
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                           rightMargin=0.75*inch, leftMargin=0.75*inch,
                           topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2ca02c'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    # Title and timestamp
    story.append(Paragraph("AI Review Analysis Report", title_style))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                          styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Get dataframe
    df = pd.DataFrame(result["ratings_dataframe"])
    
    # Summary Metrics Section
    story.append(Paragraph("Executive Summary", heading_style))
    
    metrics_data = [
        ["Metric", "Value"],
        ["Total Reviews", str(len(df))],
        ["Overall AI Rating", f"{result['overall_ai_rating']:.2f}"],
        ["Weighted Rating", f"{result['weighted_rating']:.2f}"],
        ["Mean Sentiment", f"{result['sentiment_stats']['mean_sentiment']:.3f}"],
        ["Rating Std Dev", f"{df['ai_rating'].std():.3f}"],
        ["Min Rating", f"{df['ai_rating'].min():.1f}"],
        ["Max Rating", f"{df['ai_rating'].max():.1f}"],
    ]
    
    metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
    ]))
    
    story.append(metrics_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Sentiment Breakdown
    story.append(Paragraph("Sentiment Distribution", heading_style))
    
    sentiment_counts = df["sentiment_category"].value_counts().to_dict()
    sentiment_data = [["Sentiment Category", "Count", "Percentage"]]
    
    total = len(df)
    for category in ["Strong Negative", "Negative", "Neutral", "Positive", "Strong Positive"]:
        count = sentiment_counts.get(category, 0)
        percentage = (count / total * 100) if total > 0 else 0
        sentiment_data.append([category, str(count), f"{percentage:.1f}%"])
    
    sentiment_table = Table(sentiment_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    sentiment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ca02c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
    ]))
    
    story.append(sentiment_table)
    story.append(Spacer(1, 0.3*inch))
    
    story.append(PageBreak())
    
    # Strong Outliers Section
    story.append(Paragraph("Strong Outliers Analysis", heading_style))
    
    rating_mean = df["ai_rating"].mean()
    rating_std = df["ai_rating"].std()
    threshold_low = rating_mean - (1.5 * rating_std)
    threshold_high = rating_mean + (1.5 * rating_std)
    
    strong_outliers = df[
        (df["ai_rating"] <= threshold_low) | (df["ai_rating"] >= threshold_high)
    ].to_dict("records")
    
    if strong_outliers:
        story.append(Paragraph(f"Found <b>{len(strong_outliers)}</b> strong outlier(s) "
                              f"(beyond ±1.5σ from mean)", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        for i, outlier in enumerate(strong_outliers[:5], 1):
            deviation = abs(outlier['ai_rating'] - rating_mean) / rating_std if rating_std > 0 else 0
            outlier_type = "Very Low" if outlier['ai_rating'] <= threshold_low else "Very High"
            
            outlier_text = f"""
            <b>Outlier #{i}</b> - {outlier_type} ({deviation:.2f}σ from mean)<br/>
            <b>Review ID:</b> {outlier['id']} | <b>Rating:</b> {outlier['ai_rating']} | 
            <b>Sentiment:</b> {outlier['sentiment']:.3f} ({outlier['sentiment_category']})<br/>
            <b>Review:</b> "{outlier['review_text'][:120]}..."<br/>
            <b>Reasoning:</b> {outlier['reasoning'][:150]}...<br/>
            """
            story.append(Paragraph(outlier_text, styles['BodyText']))
            story.append(Spacer(1, 0.15*inch))
    else:
        story.append(Paragraph("No strong outliers detected in this dataset.", styles['Normal']))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(PageBreak())
    
    # Top Influential Reviews
    story.append(Paragraph("Top 10 Most Influential Reviews", heading_style))
    story.append(Paragraph(
        "These reviews have the highest impact on the overall rating. Removing them would shift the average most significantly.",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.15*inch))
    
    influential = result.get("impact_analysis", {}).get("most_influential_reviews", [])
    
    if influential:
        influential_data = [["Rank", "ID", "Rating", "Sentiment", "Impact Score", "Category"]]
        
        for idx, review in enumerate(influential[:10], 1):
            influential_data.append([
                str(idx),
                str(review['id']),
                f"{review['ai_rating']:.1f}",
                f"{review['sentiment']:.2f}",
                f"{review['impact_score']:.5f}",
                review.get('sentiment_category', 'N/A')
            ])
        
        influential_table = Table(influential_data, colWidths=[0.7*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1*inch, 1.2*inch])
        influential_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff7f0e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fffacd')])
        ]))
        
        story.append(influential_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Detailed influential reviews
        story.append(Paragraph("Detailed View", ParagraphStyle(
            'subheading', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold')))
        
        for idx, review in enumerate(influential[:3], 1):
            detail_text = f"""
            <b>Review #{idx} (ID: {review['id']})</b><br/>
            Rating: {review['ai_rating']} | Sentiment: {review['sentiment']:.3f} | Impact: {review['impact_score']:.5f}<br/>
            <b>Text:</b> "{review['review_text']}"<br/>
            <b>Reasoning:</b> {review['reasoning']}<br/>
            """
            story.append(Paragraph(detail_text, styles['BodyText']))
            story.append(Spacer(1, 0.15*inch))
    
    story.append(Spacer(1, 0.5*inch))
    
    # Footer
    footer_text = (f"<i>Report generated by AI Review Analyzer | "
                  f"{len(df)} reviews analyzed | "
                  f"{datetime.now().strftime('%B %d, %Y at %H:%M')}</i>")
    story.append(Paragraph(footer_text, 
                          ParagraphStyle('footer', parent=styles['Normal'], 
                                       fontSize=9, textColor=colors.grey)))
    
    # Build PDF
    doc.build(story)
    
    return output_path
