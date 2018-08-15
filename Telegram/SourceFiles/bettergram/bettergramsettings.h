#pragma once

#include "base/observer.h"
#include <QObject>
#include <QtNetwork/QNetworkAccessManager>
#include <functional>

namespace Bettergram {

class CryptoPriceList;
class RssChannelList;
class RssChannel;
class AdItem;

/**
 * @brief The BettergramSettings class contains Bettergram specific settings
 */
class BettergramSettings : public QObject {
	Q_OBJECT

public:
	enum class BillingPlan {
		Unknown,
		Monthly,
		Quarterly,
		Yearly
	};

	static BettergramSettings *init();
	static BettergramSettings *instance();

	bool isPaid() const;
	BillingPlan billingPlan() const;

	CryptoPriceList *cryptoPriceList() const;
	RssChannelList *rssChannelList() const;
	AdItem *currentAd() const;

	bool isWindowActive() const;
	void setIsWindowActive(bool isWindowActive);

	base::Observable<void> &isPaidObservable();
	base::Observable<void> &billingPlanObservable();

	/// Download and parse crypto price list
	void getCryptoPriceList();

	/// Download and parse all RSS feeds
	void getRssChannelList();

public slots:

signals:
	void isPaidChanged();
	void billingPlanChanged();

protected:

private:
	static BettergramSettings *_instance;

	QNetworkAccessManager _networkManager;

	bool _isPaid = false;
	BillingPlan _billingPlan = BillingPlan::Unknown;

	CryptoPriceList *_cryptoPriceList = nullptr;
	RssChannelList *_rssChannelList = nullptr;
	AdItem *_currentAd = nullptr;
	bool _isWindowActive = true;
	std::function<void()> _isWindowActiveHandler = nullptr;

	base::Observable<void> _isPaidObservable;
	base::Observable<void> _billingPlanObservable;

	explicit BettergramSettings(QObject *parent = nullptr);

	void setIsPaid(bool isPaid);
	void setBillingPlan(BillingPlan billingPlan);

	void getIsPaid();
	void getNextAd(bool reset);
	void getNextAdLater(bool reset = false);

	void parseCryptoPriceList(const QByteArray &byteArray);
	bool parseNextAd(const QByteArray &byteArray);

	void getRssFeeds(const QSharedPointer<RssChannel> &channel);

private slots:
	void onGetCryptoPriceListFinished();
	void onGetCryptoPriceListSslFailed(QList<QSslError> errors);

	void onGetNextAdFinished();
	void onGetNextAdSslFailed(QList<QSslError> errors);
};

} // namespace Bettergram